from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# Module version following PEP 396
# Get version: import rodan; rodan.__version__
__version__ = '0.0.1'
