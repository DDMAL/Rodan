from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from django.conf import settings
from rodan.jobs.gamera.custom.poly_mask.celery_task import PolyMaskTask

ONEBIT = settings.ONEBIT


def load_poly_mask():
    task_class = PolyMaskTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="TO DO",
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
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
    load_poly_mask()
