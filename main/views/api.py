from django.shortcuts import render
from django.template.context_processors import request
from django.views import View
from django.http import JsonResponse
from main.business_logic.utils import get_checkout_suggestion
from main.models import Game, MultiplayerGame
import uuid

class CheckoutHintView(View):

    def get(self, request, left_score: int, throws_left: int) -> JsonResponse:
        checkout_suggestion = get_checkout_suggestion(left_score, throws_left)
        return JsonResponse({"checkout_suggestion": checkout_suggestion})

class SetNeededDartsView(View):
    def post(self, request, game_id: uuid.UUID, needed_darts: int):
        game = Game.objects.filter(id=game_id).first() or MultiplayerGame.objects.filter(id=game_id).first()
        if not game:
            raise ValueError("game not found")
        last_round = game.game_rounds.last()
        if needed_darts > 3 or needed_darts < 1:
            raise ValueError("only 1 - 3 darts are valid")
        last_round.needed_darts = needed_darts
        last_round.save()
        return render(request, 'partials/needed_darts_card.html', context={"needed_darts": needed_darts, "game": game})
