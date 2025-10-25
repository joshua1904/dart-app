from main.models import MultiplayerGame, MultiplayerPlayer
from main.utils import get_guest_names


def create_missing_players(game: MultiplayerGame):
    missing_players = game.max_players - game.game_players.count()
    guest_names = get_guest_names(missing_players)
    current_player_count = game.game_players.count()
    for counter in range(missing_players):
        MultiplayerPlayer.objects.create(
            game=game,
            player=None,
            rank=current_player_count + counter + 1,
            guest_name=guest_names[counter],
        )