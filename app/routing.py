
from django.urls import path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("realtime", ChatConsumer.as_asgi()),
]