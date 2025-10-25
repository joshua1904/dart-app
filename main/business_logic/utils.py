from main.constants import checkout_map, IMPOSSIBLE_POINTS
from main.models import Game, MultiplayerGame


def get_points_of_round(left_score: int, points: int) -> int:
    if points > 180:
        points = 180
    if points < 0:
        points = 0
    left_score = left_score - points
    if left_score < 0 or left_score == 1:
        points = 0
    if left_score == 0 and points not in checkout_map:
        points = 0
    if points in IMPOSSIBLE_POINTS:
        points = 0
    return points


def get_checkout_suggestion(left_score: int) -> str | None:
    return checkout_map.get(left_score, None)


def delete_last_round(game: Game | MultiplayerGame) -> None:
    round_to_delete = game.game_rounds.last()
    if round_to_delete:
        round_to_delete.delete()
