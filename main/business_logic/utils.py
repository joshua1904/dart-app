from django.contrib.auth.models import User

from main.constants import checkout_map, special_checkout_map, IMPOSSIBLE_POINTS
from main.models import Game, MultiplayerGame, PreferredKeyBoard, MultiplayerPlayer


def get_points_of_round(left_score: int, points: int, is_valid_checkout: bool) -> int:
    if points > 180:
        points = 180
    if points < 0:
        points = 0
    left_score = left_score - points
    if left_score < 0 or left_score == 1:
        points = 0
    if left_score == 0 and points not in checkout_map:
        points = 0
    if not is_valid_checkout and left_score == 0:
        points = 0
    if points in IMPOSSIBLE_POINTS:
        points = 0
    return points


def get_checkout_suggestion(left_score: int, throws_left: int) -> str | None:
    checkout_suggestions =  checkout_map.get(left_score, [])
    for suggestion in checkout_suggestions:
        if len(suggestion.split(" ")) <= throws_left:
            return suggestion
    return ""


def delete_last_round(game: Game | MultiplayerGame) -> None:
    round_to_delete = game.game_rounds.last()
    if round_to_delete:
        round_to_delete.delete()

def set_keyboard(user: User, keyboard: int):
    PreferredKeyBoard.objects.update_or_create(
        player=user,
        defaults={
            "keyboard": keyboard
        }
    )
def set_multiplayer_keyboard(player: MultiplayerPlayer, keyboard: int):
    if player.player:
        PreferredKeyBoard.objects.update_or_create(
            player=player.player,
            defaults={
                "keyboard": keyboard
            }
        )
        return
    PreferredKeyBoard.objects.update_or_create(
        guest_player=player,
        defaults={
            "keyboard": keyboard
        }
    )
