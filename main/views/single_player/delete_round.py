from django import views
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from main.models import Game
from main.business_logic.utils import delete_last_round


class DeleteRoundView(views.View):
    def post(self, request, game_id: int):
        game = get_object_or_404(Game, id=game_id)
        if request.user != game.player:
            return redirect(reverse_lazy("home"))
        delete_last_round(game)
        return redirect(reverse_lazy("game", kwargs={"game_id": game.id}))