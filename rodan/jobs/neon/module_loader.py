from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.models.resource import ResourceType
from rodan.jobs.neon.celery_task import PitchCorrectionTask

try:
    import pymei
except:
    raise ImportError

MEI = ResourceType.MEI


def load_segmentation():
    task_class = PitchCorrectionTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Interactive pitch correction using Neon.",
                settings=task_class.settings,
                enabled=True,
                category="Pitch Correction",
                interactive=True
                )

        j.save()

        ipt = InputPortType(job=j,
                            name=None,
                            resource_type=[MEI],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[MEI],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_segmentation()
