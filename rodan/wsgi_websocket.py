import os

import gevent.socket
import redis.connection
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer

redis.connection.socket = gevent.socket
os.environ.update(DJANGO_SETTINGS_MODULE="rodan.settings")
application = uWSGIWebsocketServer()
