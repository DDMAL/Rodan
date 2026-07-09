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

# Force the root URLconf to import now, at startup, in this synchronous context. Django
# otherwise resolves the URLconf lazily on the first request; under ASGI that runs in the
# event loop, and rodan/urls.py imports rodan.jobs.load, which executes a synchronous ORM
# query (ResourceType.objects.all()) at import time -> SynchronousOnlyOperation. Doing it
# here runs that one-time job/resource-type registration once per worker at boot instead.
from django.urls import get_resolver  # noqa: E402

get_resolver().url_patterns

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
