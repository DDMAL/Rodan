from rodan.models.job import Job
from rodan.jobs.devel import celery_task


def load_dummy_job():
    name = 'rodan.jobs.devel.dummy_job'
    if not Job.objects.filter(job_name=name).exists():
        j = Job(job_name=name,
                author="Andrew Hankinson",
                description="A Dummy Job for testing the Job loading and workflow system",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (1,), "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": (1,), "name": "output"},
                settings=[{}],
                enabled=True,
                category="Dummy",
                interactive=False
                )
        j.save()
