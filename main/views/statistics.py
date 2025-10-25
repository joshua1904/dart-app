from django import views
from django.shortcuts import render

from main.business_logic.statistics import get_singleplayer_statistics, get_multiplayer_statistics
from main.models import Game, MultiplayerGame
from main.filter.game_filter import GameFilter, MultiplayerGameFilter


class StatisticsView(views.View):
    def get(self, request):
        user = request.user
        games = Game.objects.filter(player=user)
        multiplayer_games = MultiplayerGame.objects.filter(game_players__player=user)
        filter = GameFilter(request.GET, queryset=games)
        multiplayer_filter = MultiplayerGameFilter(request.GET, queryset=multiplayer_games)
        games = filter.qs
        multiplayer_games = multiplayer_filter.qs
        if request.META.get("HTTP_HX_REQUEST"):
            return render(
                request,
                "statics/partials/statistics.detail.html",
                context={
                'singleplayer_games': games,
                'multiplayer_games': multiplayer_games,
                "singleplayer_statistics": get_singleplayer_statistics(games),
                "multiplayer_statistics": get_multiplayer_statistics(multiplayer_games, user),
                "filter": filter,
            },
            )

        return render(
            request,
            "statistics/statistics.html",
            context={
                'singleplayer_games': games,
                'multiplayer_games': multiplayer_games,
                "singleplayer_statistics": get_singleplayer_statistics(games),
                "multiplayer_statistics": get_multiplayer_statistics(multiplayer_games, user),
                "filter": filter,
            },
        )
