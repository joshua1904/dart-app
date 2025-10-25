from dataclasses import dataclass

from OpenSSL.rand import status
from django.db.models import QuerySet, Q

from main.models import Game, MultiplayerGame, Round, MultiplayerRound
from main.utils import GameStatus, MultiplayerGameStatus


@dataclass
class Statistics:
    wins: int = 0
    losses: int = 0
    total_games: int = 0
    total_points: int = 0
    total_rounds: int = 0

    @property
    def win_rate(self) -> float:
        if self.total_games == 0:
            return 0
        return round((self.wins / self.total_games) * 100, 2)

    @property
    def loss_rate(self) -> float:
        if self.total_games == 0:
            return 0
        return round((self.losses / self.total_games) * 100, 2)

    @property
    def average_points(self) -> float:
        if self.total_games == 0:
            return 0
        return round(self.total_points / self.total_rounds, 2)




def get_singleplayer_statistics(games: QuerySet[Game]) -> Statistics:
    wins = games.filter(status=GameStatus.WON.value).count()
    losses = games.filter(status=GameStatus.LOST.value).count()
    total_games = games.exclude(status=GameStatus.PROGRESS.value).count()
    total_points = sum(Round.objects.filter(game__in=games).values_list("points", flat=True))
    total_rounds = Round.objects.filter(game__in=games).count()
    return Statistics(wins, losses, total_games, total_points, total_rounds)

def get_multiplayer_statistics(games: QuerySet[MultiplayerGame], user) -> Statistics:
    wins = games.filter(winner__player=user).count()
    losses = games.filter(~Q(winner__player=user), status=MultiplayerGameStatus.FINISHED.value).count()
    total_games = games.filter(status=MultiplayerGameStatus.FINISHED.value).count()
    total_rounds = MultiplayerRound.objects.filter(game__in=games).count()
    total_points = sum(MultiplayerRound.objects.filter(game__in=games, player__player=user).values_list("points", flat=True))
    return Statistics(wins, losses, total_games, total_points, total_rounds)