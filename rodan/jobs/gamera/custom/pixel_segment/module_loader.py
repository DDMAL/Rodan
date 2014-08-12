from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.settings import RGB
from rodan.jobs.gamera.custom.pixel_segment.celery_task import PixelSegmentTask


def load_pixel_segment():
    task_class = PixelSegmentTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Ryan Bannon",
                description="TO DO",
                settings=task_class.settings,
                enabled=True,
                category="Lyric Extraction",
                interactive=True
                )

        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[RGB],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[RGB],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_pixel_segment()
