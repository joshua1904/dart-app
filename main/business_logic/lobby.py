from django.db import transaction

from main.models import MultiplayerGame, MultiplayerPlayer
from main.utils import get_guest_names, MultiplayerGameStatus


def create_missing_players(game: MultiplayerGame):
    game_players = game.game_players.all()
    game_player_count = game_players.count()
    missing_players = game.max_players - game_player_count
    missing_ids = list(
        set(i for i in range(1, game.max_players + 1))
        - set(game_players.values_list("rank", flat=True))
    )
    guest_names = get_guest_names(missing_players)
    for counter in range(missing_players):
        MultiplayerPlayer.objects.create(
            game=game,
            player=None,
            rank=missing_ids[counter],
            guest_name=guest_names[counter],
        )


def set_player_ranks(game: MultiplayerGame, data: dict):
    # data will be something like({'194-rank': '2', '195-rank': '1'}
    data = {key: value for key, value in data.items() if "-rank" in key}
    if len(data.values()) != len(set(data.values())):
        raise ValueError("PLayer have to have a different rank")
    for key, value in data.items():
        player_id = int(key.split("-")[0])
        rank = int(value)
        MultiplayerPlayer.objects.update_or_create(
            game=game, id=player_id, defaults={"rank": rank}
        )


def create_game(game: MultiplayerGame, data: dict):
    # Mark game as started
    with transaction.atomic():
        game.status = MultiplayerGameStatus.PROGRESS.value
        game.save(update_fields=["status"])
        set_player_ranks(game, data)
        create_missing_players(game)
