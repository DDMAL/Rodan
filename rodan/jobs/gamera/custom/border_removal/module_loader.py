from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from django.conf import settings
from rodan.jobs.gamera.custom.border_removal.celery_task import AutoBorderRemovalTask, CropBorderRemovalTask

ONEBIT, GREYSCALE, RGB = settings.ONEBIT, settings.GREYSCALE, settings.RGB


def load_auto_border_removal():
    task_class = AutoBorderRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Automatically tries to remove the border of a page. Non-interactive.",
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
                interactive=False
                )
        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[ONEBIT, GREYSCALE, RGB],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[ONEBIT, GREYSCALE, RGB],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_crop_border_removal():
    task_class = CropBorderRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Manual masking crop. Uses the crop interface. Interactive.",
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
                interactive=True
                )
        j.save()

        ipt = InputPortType(job=j,
                            name="input",
                            resource_type=[ONEBIT, GREYSCALE, RGB],
                            minimum=1,
                            maximum=1)
        ipt.save()

        opt = OutputPortType(job=j,
                             name="output",
                             resource_type=[ONEBIT, GREYSCALE, RGB],
                             minimum=1,
                             maximum=1)
        opt.save()


def load_module():
    load_auto_border_removal()
    load_crop_border_removal()
