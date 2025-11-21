from django import views
from django.shortcuts import render

from main.business_logic.statistics import (
 get_statistics,
)
from main.models import Game, MultiplayerGame, MultiplayerRound
from main.filter.game_filter import GameFilter, MultiplayerGameFilter


class StatisticsView(views.View):
    def get(self, request):
        user = request.user
        games = Game.objects.filter(player=user)
        multiplayer_games = MultiplayerGame.objects.filter(game_players__player=user)
        round_choices = set(games.values_list("rounds", flat=True))
        score_choices = set(games.values_list("score", flat=True))
        single_player_filter = GameFilter(
            request.GET,
            queryset=games,
            round_choices=round_choices,
            score_choices=score_choices,
        )
        multiplayer_filter = MultiplayerGameFilter(
            request.GET, queryset=multiplayer_games
        )
        games = single_player_filter.qs
        multiplayer_games = multiplayer_filter.qs
        if request.META.get("HTTP_HX_REQUEST"):
            return render(
                request,
                "statistics/partials/statistics.detail.html",
                context={
                    "singleplayer_games": games[:10],
                    "multiplayer_games": multiplayer_games[:10],
                    "statistics": get_statistics(games, multiplayer_games, user),
                    "filter": single_player_filter,
                },
            )

        return render(
            request,
            "statistics/statistics.html",
            context={
                "singleplayer_games": games[:10],
                "multiplayer_games": multiplayer_games[:10],
                "statistics": get_statistics(games, multiplayer_games, user),
                "filter": single_player_filter,
            },
        )
