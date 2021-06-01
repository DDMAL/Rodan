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


from rodan.jobs.core import (  # noqa
    create_resource,
    create_workflowrun,
    cancel_workflowrun,
    create_diva,
    redo_runjob_tree,
    retry_workflowrun,
    send_email,
    test_work,
    test_rodan_task
)
from rodan.jobs.master_task import master_task  # noqa

# Core Rodan Tasks
app.tasks.register(create_resource())
app.tasks.register(create_workflowrun())

app.tasks.register(cancel_workflowrun)
app.tasks.register(create_diva)
app.tasks.register(redo_runjob_tree)
app.tasks.register(retry_workflowrun)
app.tasks.register(send_email)
app.tasks.register(master_task)
app.tasks.register(test_work)
app.tasks.register(test_rodan_task)
#app.tasks.register(HelloWorld)
#app.tasks.register(test_task)
