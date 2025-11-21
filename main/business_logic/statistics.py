from dataclasses import dataclass
from email.policy import default

from django.db.models import QuerySet, Q, Sum, Case, When, Value, IntegerField
from django.db.models.aggregates import Count

from main.constants import checkout_map
from main.models import Game, MultiplayerGame, Round, MultiplayerRound, MultiplayerPlayer
from main.utils import GameStatus, MultiplayerGameStatus


@dataclass
class Statistics:
    wins: int = 0
    losses: int = 0
    total_games: int = 0
    total_points: int = 0
    total_rounds: int = 0
    total_darts_needed: int = 0
    sixty_plus: int = 0
    eighty_plus: int = 0
    hundred_plus: int = 0
    hundred_forty_plus: int = 0
    hundred_eighty: int = 0
    _checkout_rate: int = 0

    @property
    def win_rate(self) -> float:
        if self.total_games == 0:
            return 0
        return round((self.wins / self.total_games) * 100, 2)

    @property
    def checkout_rate(self):
        return round(self._checkout_rate, 2)
    @property
    def loss_rate(self) -> float:
        if self.total_games == 0:
            return 0
        return round((self.losses / self.total_games) * 100, 2)

    @property
    def average_points(self) -> float:
        if self.total_darts_needed == 0:
            return 0
        return round(self.total_points / self.total_darts_needed  * 3)


def _aggregate_rounds(rounds_qs):
    return rounds_qs.aggregate(
        total_points=Sum("points", default=0),
        total_rounds=Count("id"),
        total_needed_darts=Sum("needed_darts", default=0),
        sixty_plus=Count(Case(
            When(Q(points__gte=60) & Q(points__lt=80), then=Value(1))
        )),
        eighty_plus=Count(Case(
            When(Q(points__gte=80) & Q(points__lt=100), then=Value(1))
        )),
        hundred_plus=Count(Case(
            When(Q(points__gte=100) & Q(points__lt=140), then=Value(1))
        )),
        hundred_forty_plus=Count(Case(
            When(Q(points__gte=140) & Q(points__lt=180), then=Value(1))
        )),
        hundred_eighty=Count(Case(
            When(points=180, then=Value(1))
        )),
    )


def get_singleplayer_statistics(games: QuerySet[Game]) -> Statistics:
    wins = games.filter(status=GameStatus.WON.value).count()
    losses = games.filter(status=GameStatus.LOST.value).count()
    total_games = games.exclude(status=GameStatus.PROGRESS.value)
    total_rounds = _aggregate_rounds(Round.objects.filter(game__in=total_games))
    checkout_tries = sum(total_games.values_list("tried_doubles", flat=True))
    if checkout_tries:
        checkout_rate = wins / checkout_tries
    else:
        checkout_rate = 0
    return Statistics(wins, losses, total_games.count(), total_rounds.get("total_points", 0), total_rounds.get("total_rounds", 0), total_rounds.get("total_needed_darts", 0), total_rounds.get("sixty_plus", 0), total_rounds.get("eighty_plus", 0), total_rounds.get("hundred_plus", 0), total_rounds.get("hundred_forty_plus", 0), total_rounds.get("hundred_eighty", 0), checkout_rate)


def get_multiplayer_statistics(games: QuerySet[MultiplayerGame], user) -> Statistics:
    wins = games.filter(winner__player=user).count()
    losses = games.filter(
        ~Q(winner__player=user), status=MultiplayerGameStatus.FINISHED.value
    ).count()
    total_games = games.filter(status=MultiplayerGameStatus.FINISHED.value).count()
    total_rounds = _aggregate_rounds(
        MultiplayerRound.objects.filter(
            game__in=games, player__player=user
        )
    )
    checkout_tries = sum(MultiplayerPlayer.objects.filter(player=user).values_list("tried_doubles", flat=True) )
    if checkout_tries:
        checkout_rate= wins / checkout_tries
    else:
        checkout_rate = 0
    return Statistics(wins, losses, total_games, total_rounds.get("total_points", 0), total_rounds.get("total_rounds", 0), total_rounds.get("total_needed_darts", 0), total_rounds.get("sixty_plus", 0), total_rounds.get("eighty_plus", 0), total_rounds.get("hundred_plus", 0), total_rounds.get("hundred_forty_plus", 0), total_rounds.get("hundred_eighty", 0), checkout_rate)

