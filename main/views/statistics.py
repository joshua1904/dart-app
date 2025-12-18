import json

from django import views
from django.shortcuts import render

from main.business_logic.statistics import (
    get_statistics, get_avg_per_week_singleplayer, get_avg_per_week_multiplayer,
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
        game_slice = games.count() - 10 if games.count() >= 10 else 0
        multiplayer_game_slice = multiplayer_games.count() - 10 if multiplayer_games.count() >= 10 else 0
        if request.META.get("HTTP_HX_REQUEST"):
            return render(
                request,
                "statistics/partials/statistics.detail.html",
                context={
                    "singleplayer_games": games[game_slice:][::-1],
                    "multiplayer_games": multiplayer_games[multiplayer_game_slice:][::-1],
                    "statistics": get_statistics(games, multiplayer_games, user),
                    "filter": single_player_filter,
                },
            )

        return render(
            request,
            "statistics/statistics.html",
            context={
                "singleplayer_games": games[game_slice:][::-1],
                "multiplayer_games": multiplayer_games[multiplayer_game_slice:][::-1],
                "statistics": get_statistics(games, multiplayer_games, user),
                "filter": single_player_filter,
                "week_avg_singleplayer": json.dumps(get_avg_per_week_singleplayer(games)),
                "week_avg_multiplayer": json.dumps(get_avg_per_week_multiplayer(multiplayer_games))
            },
        )
