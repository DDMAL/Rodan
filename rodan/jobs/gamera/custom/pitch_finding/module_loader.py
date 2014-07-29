from rodan.models.job import Job
from rodan.jobs.gamera.custom.pitch_finding.celery_task import PitchFindingTask
from django.conf import settings

GAMERA_XML, MEI = settings.GAMERA_XML, settings.MEI


def load_pitch_finder():
    task_class = PitchFindingTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Classifies the neumes detected in the page using the classifier interface.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (GAMERA_XML,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (MEI,), "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Pitch Finding",
                interactive=False
                )

        j.save()


def load_module():
    load_pitch_finder()
