from django import views
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from main.forms.multiplayer_game_form import MultiplayerGameForm
from main.models import Session, MultiplayerGame, MultiplayerPlayer
from main.utils import MultiplayerGameStatus


class StartGame(views.View):
    def get(self, request):
        last_game = MultiplayerGame.objects.filter(creator=request.user).first()
        score = last_game.score if last_game else 301
        form = MultiplayerGameForm(
            initial={"max_players": 2, "online": False, "score": score}
        )
        progress_games = MultiplayerGame.objects.filter(
            game_players__player=request.user
        ).exclude(status=MultiplayerGameStatus.FINISHED.value)[:5]
        return render(
            request,
            "multiplayer/start_game.html",
            context={"form": form, "progress_games": progress_games},
        )

    def post(self, request):
        form = MultiplayerGameForm(request.POST)
        if not form.is_valid():
            return render(
                request, "multiplayer/start_game.html", context={"form": form}
            )
        session = Session.objects.create(first_to=form.cleaned_data["first_to"])
        online = form.cleaned_data["online"]
        max_players = form.cleaned_data["max_players"]
        game = MultiplayerGame.objects.create(
            score=form.cleaned_data["score"],
            max_players=max_players,
            online=online,
            session=session,
            creator=request.user,
            status=(
                MultiplayerGameStatus.WAITING.value
                if max_players > 1
                else MultiplayerGameStatus.PROGRESS.value
            ),
            one_device_manage=form.cleaned_data["one_device_manage"],
        )
        # Add the creator as the first player

        MultiplayerPlayer.objects.create(
            game=game,
            player=request.user,
            rank=1,
        )
        if max_players == 1:
            return redirect(
                reverse_lazy("multiplayer_game", kwargs={"game_id": game.id})
            )

        return redirect(reverse_lazy("lobby", kwargs={"game_id": game.id}))
