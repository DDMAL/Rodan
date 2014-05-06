from rodan.models.job import Job
from django.conf import settings

from rodan.jobs.neon.celery_task import PitchCorrectionTask


def load_module():
    task_class = PitchCorrectionTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Interactive pitch correction using Neon.",
                input_types={"default": None, "has_default": False,
                             "list_of": False, "pixel_types": (settings.MEI,),
                             "name": "input"},
                output_types={"default": None, "has_default": False,
                              "list_of": False, "pixel_types": (settings.MEI,),
                              "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Pitch Correction",
                interactive=True
                )

        j.save()
