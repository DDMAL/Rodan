from rodan.models.job import Job
from rodan.jobs.gamera.custom.neume_classification.celery_task import JOB_NAME_MANUAL
from rodan.settings import ONEBIT


def load_manual_classifier():
    job = Job.objects.filter(job_name=JOB_NAME_MANUAL)
    if job.exists():
        return None
    else:
        settings = []

        j = Job(job_name=JOB_NAME_MANUAL,
                author="Deepanjan Roy",
                description="Classifies the neumes detected in the page.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "output"},
                settings=settings,
                enabled=True,
                category="Classification",
                interactive=True
                )

        j.save()


def load_module():
    load_manual_classifier()
