from __future__ import absolute_import
import os

import django
from django.conf import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rodan.settings")
django.setup()

app = Celery("rodan")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


from rodan.jobs.core import (  # noqa
    create_resource,
    create_workflowrun,
    cancel_workflowrun,
    create_diva,
    redo_runjob_tree,
    retry_workflowrun,
    send_email,
    send_templated_email,
)
from rodan.jobs.master_task import master_task  # noqa

# Core Rodan Tasks.
# create_resource / create_workflowrun are Task *subclasses* (not auto-registered), so
# register an instance of each explicitly.
app.register_task(create_resource())
app.register_task(create_workflowrun())

# cancel_workflowrun, create_diva, redo_runjob_tree, retry_workflowrun, send_email,
# send_templated_email and master_task are @shared_task functions. Importing them (above)
# already auto-registers them with this app. They must NOT be manually registered: a
# @shared_task is a promise proxy, and registering the proxy stores it under its own name
# in the registry, so a later lookup resolves the proxy to itself — an infinite loop
# (RecursionError in celery.local). Celery 5 binds shared tasks to the app on finalize.
