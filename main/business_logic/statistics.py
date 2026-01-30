from dataclasses import dataclass
from django.db.models import QuerySet, Q, Sum, Case, When, Value, Avg
from django.db.models.aggregates import Count
from django.db.models.functions import TruncWeek

from main.models import Game, MultiplayerGame, Round, MultiplayerRound, MultiplayerPlayer
from main.utils import GameStatus, MultiplayerGameStatus

from datetime import datetime





@dataclass(frozen=True)
class PartStatistics:
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
    twenty_six: int = 0

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
        if self.total_darts_needed == 0:
            return 0
        return round(self.total_points / self.total_darts_needed  * 3)


@dataclass(frozen=True)
class Statistics:
    single_player: PartStatistics
    multiplayer: PartStatistics
    checkout_rate: float

    @property
    def sixty_plus(self):
        return self.single_player.sixty_plus + self.multiplayer.sixty_plus
    @property
    def eighty_plus(self):
        return self.single_player.eighty_plus + self.multiplayer.eighty_plus
    @property
    def hundred_plus(self):
        return self.single_player.hundred_plus + self.multiplayer.hundred_plus
    @property
    def hundred_forty_plus(self):
        return self.single_player.hundred_forty_plus + self.multiplayer.hundred_forty_plus
    @property
    def hundred_eighty(self):
        return self.single_player.hundred_eighty + self.multiplayer.hundred_eighty
    @property
    def twenty_six(self):
        return self.single_player.twenty_six + self.multiplayer.twenty_six

    


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
        twenty_six=Count(Case(
            When(points=26, then=Value(1))
        ))
    )


def get_singleplayer_statistics(games: QuerySet[Game]) -> PartStatistics:
    wins = games.filter(status=GameStatus.WON.value).count()
    losses = games.filter(status=GameStatus.LOST.value).count()
    total_games = games.exclude(status=GameStatus.PROGRESS.value)
    total_rounds = _aggregate_rounds(Round.objects.filter(game__in=total_games))
    return PartStatistics(wins, losses, total_games.count(), total_rounds.get("total_points", 0), total_rounds.get("total_rounds", 0), total_rounds.get("total_needed_darts", 0), total_rounds.get("sixty_plus", 0), total_rounds.get("eighty_plus", 0), total_rounds.get("hundred_plus", 0), total_rounds.get("hundred_forty_plus", 0), total_rounds.get("hundred_eighty", 0), total_rounds.get("twenty_six", 0))


def get_multiplayer_statistics(games: QuerySet[MultiplayerGame], user) -> PartStatistics:
    wins = games.filter(winner__player=user).count()
    losses = games.filter(
        ~Q(winner__player=user), status=MultiplayerGameStatus.FINISHED.value
    ).count()
    total_games = games.filter(status=MultiplayerGameStatus.FINISHED.value).count()
    total_rounds = _aggregate_rounds(
        MultiplayerRound.objects.filter(
            game__in=games
        )
    )
    return PartStatistics(wins, losses, total_games, total_rounds.get("total_points", 0), total_rounds.get("total_rounds", 0), total_rounds.get("total_needed_darts", 0), total_rounds.get("sixty_plus", 0), total_rounds.get("eighty_plus", 0), total_rounds.get("hundred_plus", 0), total_rounds.get("hundred_forty_plus", 0), total_rounds.get("hundred_eighty", 0), total_rounds.get("twenty_six", 0))


def get_checkout_rate(singleplayer_games: QuerySet[Game], multiplayer_games: QuerySet[MultiplayerGame], user) -> float:
    singleplayer_checkout_info = singleplayer_games.aggregate(total_tries=Sum("tried_doubles", default=0), wins=Count("id", filter=Q(tried_doubles__gt=0)))
    multiplayer_checkout_info= MultiplayerPlayer.objects.filter(game__in=multiplayer_games, player=user).aggregate(total_tries=Sum("tried_doubles", default=0), wins=Count("id", filter=Q(tried_doubles__gt=0)))
    wins = singleplayer_checkout_info.get("wins", 0) + multiplayer_checkout_info.get("wins", 0)
    checkout_tries =singleplayer_checkout_info.get("total_tries", 0) + multiplayer_checkout_info.get("total_tries", 0)
    if checkout_tries == 0:
        return 0.0
    return round(wins / checkout_tries * 100, 2)

def get_statistics(games: QuerySet[Game], multiplayer_games: QuerySet[MultiplayerGame], user) -> Statistics:
    singleplayer_statistics = get_singleplayer_statistics(games)
    multiplayer_statistics = get_multiplayer_statistics(multiplayer_games, user)
    checkout_rate= get_checkout_rate(games, multiplayer_games, user)
    return Statistics(singleplayer_statistics, multiplayer_statistics, checkout_rate)

def get_avg_per_week_singleplayer(games: QuerySet[Game]):
    rounds = Round.objects.filter(game__in=games)
    return _get_avg_json(rounds)
def get_avg_per_week_multiplayer(games: QuerySet[MultiplayerGame]):
    rounds = MultiplayerRound.objects.filter(game__in=games)
    return _get_avg_json(rounds)

def _get_avg_json(rounds: QuerySet[MultiplayerRound] | QuerySet[Round]) -> list:
    week_avgs = rounds.annotate(
        week=TruncWeek("game__date")).values("week").annotate(avg=Avg("points")).order_by("week")
    return [{"x": datetime.strftime(i.get('week'), '%Y-%W'), "y": i.get("avg")} for i in week_avgs]