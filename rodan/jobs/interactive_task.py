from rodan.jobs.base import RodanTask

class InteractiveTask(RodanTask):
    name = 'rodan.core.interactive_task'
    author = "Ling-Xiao Yang"
    description = "General interactive task."
    settings = []
    enabled = True
    category = "Core"
    interactive = True

    input_port_types = [{
        'name': 'resource',
        'resource_types': lambda t: True,  # any type of data
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'directive',
        'resource_types': ['application/vnd.rodan.interactive.directive+json'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'result',
        'resource_types': ['application/vnd.rodan.interactive.result+json'],
        'minimum': 1,
        'maximum': 1
    }]


    def run(self, *a, **k):
        # Do nothing. Output is stored by interactive view. This task should never be executed in Celery.
        raise RuntimeError('Interactive task is executed in Celery!')
