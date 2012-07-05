import celery
from collections import OrderedDict
from celery.execute import send_task
from djcelery.snapshot import Camera

from django.conf import settings

import json
import string

from djcelery.models import TaskState
from rodan.models.results import Result, ResultTask
from rodan.models.projects import Page


class RodanMonitor(Camera):

    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.states = OrderedDict()
        self.expire_states = {
                celery.states.SUCCESS: settings.CELERYCAM_EXPIRE_SUCCESS,
                celery.states.EXCEPTION_STATES: settings.CELERYCAM_EXPIRE_ERROR,
                celery.states.UNREADY_STATES: settings.CELERYCAM_EXPIRE_PENDING,
        }

    def restart(self, task):
        print "req"
        tname = task.name

        # HACK - args is a string, but we know it looks like a tuple
        # with the result ID as the first (only) param - (4,)
        a = task.args[1:-1]
        parts = a.split(",")

        orig_kw = json.loads(task.kwargs.replace("'", "\""))

        # need to remake (immutable strings in python right?) the kw to avoid unicode in the keys (after the first restart, unicode 'u's will appear in the incoming kwargs string)
        kw = dict((k.encode('ascii'), v) for (k, v) in orig_kw.items())

        print "restarting task", tname
        print a, kw

        send_task(tname, [int(parts[0])], kw)

    def log(self, task_id, task):
        t = TaskState.objects.get(task_id=task_id)
        args = task.args
        if "misc_tasks" not in task.name:
            # HACK - args is a string, but we know it looks like a tuple
            # with the result ID as the first (only) param - (4,)
            x = args[1:-1]
            parts = x.split(",")
            result_id = int(parts[0])
            print "RESID::%s\n" % result_id
            result = Result.objects.get(pk=result_id)

            rtask, created = ResultTask.objects.get_or_create(result=result, task=t)

    def success(self, task):
        args = task.args
        if "misc_tasks" in task.name:
            if "create_thumbnails_task" in task.name:
                mt_id = args[1:string.find(args, ",")]
                page_id = int(mt_id)
                page = Page.objects.get(pk=page_id)
                print "Page is_ready(before): %s" % page.is_ready
                page.is_ready = True
                page.save()
                print "Page is_ready(after): %s" % page.is_ready

    def on_shutter(self, state):
        Camera.on_shutter(self, state)
        if not state.event_count:
            return

        for taskid, task in state.tasks.iteritems():
            print taskid
            self.log(taskid, task)

            if taskid in self.states:
                oldstate = self.states[taskid]
                if task.state != oldstate:
                    print "  state changed"
                    print "    to", task.state
                    self.states[taskid] = task.state
                    if task.state == "SUCCESS":
                        self.success(task)
                    if task.state == "FAILURE":
                        self.restart(task)
            else:
                print "  new task"
                self.states[taskid] = task.state
