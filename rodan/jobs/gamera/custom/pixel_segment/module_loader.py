from rodan.models.job import Job
from rodan.settings import RGB
from rodan.jobs.gamera.custom.pixel_segment.celery_task import PixelSegmentTask


def load_pixel_segment():
    task_class = PixelSegmentTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Ryan Bannon",
                description="TO DO",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (RGB,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (RGB,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Lyric Extraction",
                interactive=True
                )

        j.save()


def load_module():
    load_pixel_segment()
