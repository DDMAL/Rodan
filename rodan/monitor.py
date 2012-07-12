import celery
from collections import OrderedDict
from djcelery.snapshot import Camera

from django.conf import settings

from djcelery.models import TaskState
from rodan.models.results import Result, ResultTask


class RodanMonitor(Camera):

    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.states = OrderedDict()
        self.expire_states = {
                celery.states.SUCCESS: settings.CELERYCAM_EXPIRE_SUCCESS,
                celery.states.EXCEPTION_STATES: settings.CELERYCAM_EXPIRE_ERROR,
                celery.states.UNREADY_STATES: settings.CELERYCAM_EXPIRE_PENDING,
        }

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
            result = Result.objects.select_for_update().get(pk=result_id)
            result.task_state = t.state
            result.save()
            rtask, created = ResultTask.objects.get_or_create(result=result, task=t)

    def on_shutter(self, state):
        Camera.on_shutter(self, state)
        if not state.event_count:
            return

        for taskid, task in state.tasks.iteritems():
            print taskid
            self.log(taskid, task)
