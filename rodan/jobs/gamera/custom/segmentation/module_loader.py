from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.jobs.gamera.custom.segmentation.celery_task import SegmentationTask
from rodan.models.resource import ResourceType

ONEBIT = ResourceType.ONEBIT


def load_segmentation():
    task_class = SegmentationTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Finds the staves using Miyao Staff Finder and masks out everything else.",
                settings=task_class.settings,
                enabled=True,
                category="Segmentation",
                interactive=True
                )

        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[ONEBIT],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[ONEBIT],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_segmentation()
