from django import views
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from main.forms.game_form import GameForm
from main.models import Game
from main.utils import GameStatus


class StartGame(views.View):
    def get(self, request):
        last_game = Game.objects.filter(player=request.user).first()
        form = GameForm(initial={"rounds": last_game.rounds if last_game else 3 , "score": last_game.score if last_game else 121})
        progress_games = Game.objects.filter(
            player=request.user, status=GameStatus.PROGRESS.value
        ).order_by("-date")
        return render(
            request,
            "single_player/start_game.html",
            context={
                "form": form,
                "progress_games": progress_games,
            },
        )

    def post(self, request):
        form = GameForm(request.POST)
        if not form.is_valid():
            return redirect(reverse_lazy("singleplayer"))

        game = form.save(commit=False)
        game.player = request.user
        game.save()
        return redirect(reverse_lazy("game", kwargs={"game_id": game.id}))
