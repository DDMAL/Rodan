"""
WebSocket consumer that replaces django-websocket-redis (ws4redis).

Rodan's live status updates are produced by a Postgres ``plpython3u`` trigger
(see ``rodan/models/__init__.py``) that ``redis.publish``es row-change events to the
``WEBSOCKET_BROADCAST_CHANNEL`` Redis channel. ws4redis used to relay that channel to
browser websockets; this consumer does the same with Django Channels: on connect it
subscribes to the Redis channel and forwards every published message to the client.

Server -> client only (status broadcasts); inbound frames are ignored, which preserves
the behaviour the Backbone client relies on (it only subscribes to broadcasts).
"""
import asyncio

import redis.asyncio as aioredis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        conn = settings.WS4REDIS_CONNECTION
        self._redis = aioredis.Redis(
            host=conn["host"],
            port=int(conn["port"]),
            db=int(conn["db"]),
        )
        self._pubsub = self._redis.pubsub()
        channel = getattr(settings, "WEBSOCKET_BROADCAST_CHANNEL", "rodan:broadcast:rodan")
        await self._pubsub.subscribe(channel)
        self._reader_task = asyncio.create_task(self._relay())

    async def _relay(self):
        try:
            async for message in self._pubsub.listen():
                if message and message.get("type") == "message":
                    data = message["data"]
                    if isinstance(data, (bytes, bytearray)):
                        data = data.decode("utf-8", "replace")
                    await self.send(text_data=data)
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        # Status stream is server -> client only; ignore anything the client sends.
        return

    async def disconnect(self, code):
        task = getattr(self, "_reader_task", None)
        if task is not None:
            task.cancel()
        pubsub = getattr(self, "_pubsub", None)
        if pubsub is not None:
            try:
                await pubsub.aclose()
            except Exception:
                pass
        client = getattr(self, "_redis", None)
        if client is not None:
            try:
                await client.aclose()
            except Exception:
                pass
