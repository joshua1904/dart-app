from django import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from main.forms.multiplayer_game_form import MultiplayerGameForm
from main.models import Session, MultiplayerGame, MultiplayerPlayer


class StartGame(views.View):
    def get(self, request):
        form = MultiplayerGameForm(
            initial={"max_players": 2, "online": False, "score": 301}
        )
        return render(request, "multiplayer/start_game.html", context={"form": form})

    def post(self, request):
        form = MultiplayerGameForm(request.POST)
        if not form.is_valid():
            return render(
                request, "multiplayer/start_game.html", context={"form": form}
            )
        session = Session.objects.create(first_to=form.cleaned_data["first_to"])
        game = MultiplayerGame.objects.create(
            score=form.cleaned_data["score"],
            max_players=form.cleaned_data["max_players"],
            online=form.cleaned_data["online"],
            session=session,
            creator=request.user,
        )
        # Add the creator as the first player

        MultiplayerPlayer.objects.create(
            game=game,
            player=request.user,
            rank=1,
        )
        return redirect(reverse_lazy("lobby", kwargs={"game_id": game.id}))
