from rodan.models.job import Job
from django.conf import settings

from rodan.jobs.gamera.custom.segmentation.celery_task import SegmentationTask

ONEBIT = settings.ONEBIT


def load_segmentation():
    task_class = SegmentationTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Finds the staves using Miyao Staff Finder and masks out everything else.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Segmentation",
                interactive=True
                )

        j.save()


def load_module():
    load_segmentation()
