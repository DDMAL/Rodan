"""
ASGI config for Rodan.

Serves HTTP (Django) and WebSocket (Channels) from one application. The websocket
side replaces the retired django-websocket-redis (ws4redis): the BroadcastConsumer
relays the Redis pub/sub channel that the Postgres plpython3 trigger publishes to.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rodan.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

# Initialise Django (populates apps) before importing anything that touches models/settings.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.urls import re_path  # noqa: E402

from rodan.consumers import BroadcastConsumer  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Matches the client's connection to /ws/rodan?subscribe-broadcast&... (SocketUpdater.js).
        "websocket": URLRouter(
            [
                re_path(r"^ws/", BroadcastConsumer.as_asgi()),
            ]
        ),
    }
)
