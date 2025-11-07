from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg
import logging
from main.business_logic.utils import get_points_of_round, get_checkout_suggestion
from main.models import MultiplayerGame, MultiplayerPlayer, MultiplayerRound, Session, PreferredKeyBoard
from main.utils import MultiplayerGameStatus
from collections import defaultdict

logger = logging.getLogger(__name__)


def get_game_info(game_id: int):
    game = get_object_or_404(MultiplayerGame, id=game_id)
    return game


def get_turn(game) -> int:
    last_turn = game.game_rounds.order_by("id").last()
    # if no rounds, return 1
    if not last_turn or game.max_players == 1:
        return 1
    last_rank = last_turn.player.rank
    if last_rank == game.max_players:
        return 1
    return last_rank + 1


def get_left_score(game, game_player) -> int:
    total_points = game.game_rounds.filter(player=game_player).aggregate(
        total_points=Sum("points")
    )["total_points"]
    # If no rounds exist, total_points will be None, so default to 0
    if total_points is None:
        total_points = 0
    return game.score - total_points


def get_queue(game, turn: int) -> list:
    queue = list(game.game_players.order_by("rank").values_list("rank", flat=True))
    return queue[turn:] + queue[: turn - 1]


def get_wins(session: Session | None, player: MultiplayerPlayer) -> int:
    if not session:
        # currently sessions can be null
        return 0
    # Filter by the actual User, not the MultiplayerPlayer instance
    if player.player:  # Check if it's not a guest
        return session.games.filter(winner__player=player.player).count()
    else:  # For guest players, filter by guest_name
        return session.games.filter(winner__guest_name=player.guest_name).count()


def get_game_context(game) -> dict:
    current_user = get_object_or_404(MultiplayerPlayer, game=game, rank=get_turn(game))
    queue_list = []
    for rank in get_queue(game, current_user.rank):
        player = game.game_players.get(rank=rank)
        queue_list.append(
            {
                "player": player,
                "left_score": get_left_score(game, player),
                "checkout_suggestion": get_checkout_suggestion(
                    get_left_score(game, player)
                ),
                "wins": get_wins(game.session, player),
            }
        )
    last_round = game.game_rounds.order_by("id").last()
    last_points = last_round.points if last_round else None
    preferred_keyboard = PreferredKeyBoard.objects.filter(player=current_user.player).first()
    keyboard = preferred_keyboard.keyboard if preferred_keyboard else 0
    return {
        "game": game,
        "turn": current_user,
        "left_score": get_left_score(game, current_user),
        "checkout_suggestion": get_checkout_suggestion(
            get_left_score(game, current_user)
        ),
        "average_points": get_average_points(game, current_user),
        "wins": get_wins(game.session, current_user),
        "queue": queue_list,
        "last_points": last_points,
        "keyboard": keyboard,
    }


def add_round(game, player, points) -> bool:
    left_score = get_left_score(game, player)
    points = get_points_of_round(left_score, points)
    MultiplayerRound(game=game, player=player, points=points).save()
    if left_score == points:
        game.status = MultiplayerGameStatus.FINISHED.value
        game.winner = player
        game.save()
        return True
    return False


def get_average_points(game, player) -> float:
    return game.game_rounds.filter(player=player).aggregate(
        average_points=Avg("points")
    )["average_points"]


def get_needed_rounds(game, player) -> int:
    return game.game_rounds.filter(player=player).count()


def get_players_ordered_by_wins(session: Session) -> list:
    winner_dict = defaultdict(int)
    for game in session.games.all():
        if game.winner.player:
            winner_dict[game.winner.player.username] += 1
        else:
            winner_dict[game.winner.guest_name] += 1
    for player in session.games.first().game_players.all():
        winner_dict[player.player.username if player.player else player.guest_name] += 0
    return sorted(winner_dict.items(), key=lambda x: x[1], reverse=True)


def get_ending_context(game) -> dict:

    winner_stats = {
        "average_points": get_average_points(game, game.winner),
        "needed_rounds": get_needed_rounds(game, game.winner),
    }
    return {
        "game": game,
        "winner": game.winner,
        "winner_stats": winner_stats,
        "players": get_players_ordered_by_wins(game.session),
        "session_won": game.session.first_to
        and get_wins(game.session, game.winner) == game.session.first_to,
    }


def create_follow_up_game(game: MultiplayerGame) -> MultiplayerGame:
    # create also new session if session was won
    session = game.session
    if game.winner and game.session and game.session.first_to:
        wins = get_wins(game.session, game.winner)
        if wins == game.session.first_to:
            session = Session.objects.create(first_to=game.session.first_to)

    new_game = MultiplayerGame(
        score=game.score,
        creator=game.creator,
        max_players=game.max_players,
        online=game.online,
        status=MultiplayerGameStatus.PROGRESS.value,
        session=session,
    )
    new_game.save()

    for player in game.game_players.all():
        possible_new_rank = player.rank - 1
        new_rank = possible_new_rank if possible_new_rank != 0 else game.max_players
        MultiplayerPlayer.objects.create(
            game=new_game,
            player=player.player,
            rank=new_rank,
            guest_name=player.guest_name,
        )
        logger.info(f"New game created: {new_game.id}")
    return new_game
