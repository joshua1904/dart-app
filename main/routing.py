from django.urls import path
from .consumers import GameConsumer, LobbyConsumer

websocket_urlpatterns = [
    path("ws/lobby/<uuid:game_id>/", LobbyConsumer.as_asgi()),
    path("ws/<uuid:game_id>/", GameConsumer.as_asgi()),
]
