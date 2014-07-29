from rodan.models.job import Job
from rodan.jobs.diva.celery_task import JOB_NAME


def load_module():
    job = Job.objects.filter(job_name=JOB_NAME)
    if job.exists():
        return None
    else:
        j = Job(job_name=JOB_NAME,
                author="Andrew Hankinson",
                description="Converts an image to a JPEG2000 image suitable for display in Diva",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [3], "name": None},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [7], "name": "output"},
                settings={},
                enabled=True,
                category="Conversion",
                interactive=False
                )

        j.save()
