from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, connection
from django.shortcuts import render, redirect
from django.views import View

from main.models import Game, MultiplayerGame, MultiplayerPlayer, PreferredKeyBoard


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, View):
    template_name = "registration/delete_account.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = request.user
        with transaction.atomic():
            MultiplayerPlayer.objects.filter(player=user).update(player=None, guest_name="deleted")
            PreferredKeyBoard.objects.filter(player=user).delete()
            Game.objects.filter(player=user).delete()
            user.delete()
        logout(request)
        return redirect("login")


