from __future__ import absolute_import
import os

import django
from django.conf import settings
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rodan.settings')
django.setup()

app = Celery('rodan')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
