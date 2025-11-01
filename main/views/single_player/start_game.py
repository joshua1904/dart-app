from django import views
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from main.forms.game_form import GameForm
from main.models import Game
from main.utils import GameStatus


class StartGame(views.View):
    def get(self, request):
        form = GameForm(initial={"rounds": 3, "score": 121})
        progress_games = Game.objects.filter(
            player=request.user, status=GameStatus.PROGRESS.value
        )
        return render(
            request,
            "single_player/start_game.html",
            context={
                "rounds": 3,
                "score": 121,
                "form": form,
                "progress_games": progress_games,
            },
        )

    def post(self, request):
        form = GameForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "single_player/start_game.html",
                context={"rounds": 3, "score": 121, "form": form},
            )

        game = form.save(commit=False)
        game.player = request.user
        game.save()
        return redirect(reverse_lazy("game", kwargs={"game_id": game.id}))
