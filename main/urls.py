from django.urls import path
from django.contrib.auth.decorators import login_required

from main.views.api import SetSinglePlayerCheckoutMissView, SetMultiplayerCheckoutMissView
from .views import (
    HomeView,
    StartGame,
    GameView,
    ResultView,
    StatisticsView,
    MultiplayerStartGame,
    Lobby,
    MultiplayerGameView,
    MultiplayerGameOverviewView,
    DeleteRoundView,
    SignUpView,
    CheckoutHintView,
    SetNeededDartsView,
)

home_urlpatterns = [
    path("", login_required(HomeView.as_view()), name="home"),
    path(
        "statistics/",
        login_required(StatisticsView.as_view()),
        name="statistics",
    ),
]
help_urlpatterns = [
    path("checkout-hint/<int:left_score>/<int:throws_left>/", CheckoutHintView.as_view(), name="checkout_hint"),
    path("set-needed-darts/singleplayer/<uuid:game_id>/<int:needed_darts>/", SetNeededDartsView.as_view(), name="set-needed-darts-singleplayer"),
    path("set-checkout-misses/singleplayer/<uuid:game_id>/<str:operator>/", SetSinglePlayerCheckoutMissView.as_view(), name="set-checkout-misses-singleplayer"),
    path("set-checkout-misses/multiplayer/<int:player_id>/<str:operator>/", SetMultiplayerCheckoutMissView.as_view(), name="set-checkout-misses-multiplayer"),

]

single_player_urlpatterns = [
    path("singleplayer/", login_required(StartGame.as_view()), name="singleplayer"),
    path(
        "singleplayer/game/<uuid:game_id>/",
        login_required(GameView.as_view()),
        name="game",
    ),
    path(
        "singleplayer/results/<uuid:game_id>/",
        login_required(ResultView.as_view()),
        name="result",
    ),
    path(
        "singleplayer/game/<uuid:game_id>/delete_round/",
        login_required(DeleteRoundView.as_view()),
        name="delete_round",
    ),
]

multiplayer_urlpatterns = [
    path(
        "multiplayer/",
        login_required(MultiplayerStartGame.as_view()),
        name="multiplayer",
    ),
    path(
        "multiplayer/lobby/<uuid:game_id>/",
        login_required(Lobby.as_view()),
        name="lobby",
    ),
    path(
        "multiplayer/game/<uuid:game_id>/",
        login_required(MultiplayerGameView.as_view()),
        name="multiplayer_game",
    ),
    path(
        "multiplayer/game/<uuid:game_id>/overview/",
        login_required(MultiplayerGameOverviewView.as_view()),
        name="multiplayer_game_overview",
    ),
]

urlpatterns = home_urlpatterns + single_player_urlpatterns + multiplayer_urlpatterns + help_urlpatterns

# Auth related (signup)
urlpatterns += [
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
]
