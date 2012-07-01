from collections import OrderedDict
from celery.execute import send_task
from celery.events.snapshot import Polaroid

class RodanMonitor(Polaroid):

    def __init__(self, *args, **kwargs):
        Polaroid.__init__(self, *args, **kwargs)
        self.states = OrderedDict()

    def restart(self, task):
        print "req"
        tname = task.name
        a = task.args
        kw = task.kwargs
        print "restarting task",tname
        print a,kw
        send_task(tname, *a, **kw)

    def on_shutter(self, state):
        for taskid, task in state.tasks.iteritems():
            print taskid
            if taskid in self.states:
                oldstate = self.states[taskid]
                if task.state != oldstate:
                    print "  state changed"
                    print "    to",task.state
                    self.states[taskid] = task.state
                    if task.state == "FAILURE":
                        print "Task failed!!"
                        self.restart(task)
            else:
                print "  new task"
                self.states[taskid] = task.state
