from rodan.models.job import Job
from rodan.jobs.border_removal.celery_task import JOB_NAME
#from celery import registry


def load_module():
    #registry.tasks.register(celery_task.BorderRemovalAutoTask)
    job = Job.objects.filter(job_name=JOB_NAME)
    if job.exists():
        return None
    else:
        j = Job(job_name=JOB_NAME,
                author="Deepanjan Roy",
                description="Automatically tries to remove the border of a page. Non-interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [1], "name": "greyscale"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [1], "name": "greyscale"},
                settings={},
                enabled=True,
                category="Border Removal",
                interactive=False
                )

        j.save()
