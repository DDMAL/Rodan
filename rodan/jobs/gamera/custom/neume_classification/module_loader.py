from rodan.models.job import Job
from rodan.jobs.gamera.custom.neume_classification.celery_task import ManualClassificationTask, AutoClassificationTask
from django.conf import settings

ONEBIT, GAMERA_XML = settings.ONEBIT, settings.GAMERA_XML


def load_manual_classification():
    task_class = ManualClassificationTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Classifies the neumes detected in the page using the classifier interface.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (GAMERA_XML,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Classification",
                interactive=True
                )

        j.save()

def load_automatic_classification():
    task_class = AutoClassificationTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Automatically classifies the neumes detected in the page using the classifier provided.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (ONEBIT,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (GAMERA_XML,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Classification",
                interactive=False
                )

        j.save()


def load_module():
    load_manual_classification()
    load_automatic_classification()
