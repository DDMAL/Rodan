from rodan.models.job import Job
from rodan.settings import ONEBIT
from rodan.jobs.gamera.custom.poly_mask.celery_task import PolyMaskTask


def load_poly_mask():
    task_class = PolyMaskTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="TO DO",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
                interactive=True
                )

        j.save()


def load_module():
    load_poly_mask()
