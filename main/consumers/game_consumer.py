import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from main.business_logic.utils import delete_last_round, set_keyboard, set_multiplayer_keyboard, get_needed_darts
from main.models import MultiplayerGame
from django.template.loader import render_to_string
from urllib.parse import parse_qs
from main.business_logic.multiplayer_game import (
    get_game_context,
    get_turn,
    add_round,
    create_follow_up_game,
)
import logging

logger = logging.getLogger(__name__)


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]

        # Check if user is authenticated
        if not self.user.is_authenticated:
            self.close()
            return

        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game = MultiplayerGame.objects.get(id=self.game_id)
        async_to_sync(self.channel_layer.group_add)(
            str(self.game_id), self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            str(self.game_id), self.channel_name
        )

    def new_game(self):
        new_game = create_follow_up_game(self.game)
        self.create_redirect_all_event(f"/multiplayer/game/{new_game.id}/")

    def receive(self, text_data):
        data = {}
        # Try JSON first (manual sends)
        try:
            data = json.loads(text_data)
        except Exception:
            # Fallback to form-encoded (htmx ws-send)
            try:
                parsed = {
                    k: v[0] if isinstance(v, list) and v else v
                    for k, v in parse_qs(text_data).items()
                }
                data.update(parsed)
            except Exception:
                pass
        user = self.scope["user"]
        keyboard = int(data.get("keyboard") or 0)
        action = data.get("action")
        if action == "new_game":
            self.new_game()
            return
        if action == "delete_last_round":
            delete_last_round(self.game)
            self.update_content_event()
            return
        points = data.get("points")
        if not points:
            points = 0
        player = self.game.game_players.get(rank=get_turn(self.game))
        set_multiplayer_keyboard(player, keyboard)
        if (
            player.player != user
            and player.player != None
            and not self.game.one_device_manage
        ):
            logger.warning(f"Player {player.player} is not the current player")
            return
        ended_with_double = data.get("ended_with_double") == "true"
        is_valid_checkout = (ended_with_double and keyboard == 1) or keyboard == 0
        needed_darts = get_needed_darts(data)
        # add round returns true if game is ended
        if add_round(self.game, player, int(points), is_valid_checkout, needed_darts):

            self.create_redirect_all_event(
                f"/multiplayer/game/{self.game_id}/overview/"
            )
            return

        self.update_content_event()

    def send_game_content(self, event):
        game_id = event["game_id"]
        game = MultiplayerGame.objects.get(id=game_id)
        context = get_game_context(game)
        context["user"] = self.scope["user"]
        html = render_to_string(
            "multiplayer/game/partials/game_card.html", context=context
        )
        self.send(
            text_data=f'<div id="game-content" hx-swap-oob="innerHTML">{html}</div>'
        )

    def redirect_all(self, event):
        url = event["url"]
        # Send JSON message with redirect instruction
        redirect_message = {"type": "redirect", "url": url}
        self.send(text_data=json.dumps(redirect_message))

    def create_redirect_all_event(self, url: str):
        event = {
            "type": "redirect_all",
            "url": url,
        }
        async_to_sync(self.channel_layer.group_send)(str(self.game_id), event)

    def update_content_event(self):
        event = {"type": "send_game_content", "game_id": self.game_id}
        async_to_sync(self.channel_layer.group_send)(str(self.game_id), event)
