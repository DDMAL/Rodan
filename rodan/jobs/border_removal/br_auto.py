from rodan.models.job import Job
from rodan.jobs.border_removal.celery_task import JOB_NAME
from rodan.jobs.gamera import argconvert
from gamera.toolkits.border_removal.plugins.border_removal import border_removal


def load_module():
    job = Job.objects.filter(job_name=JOB_NAME)
    if job.exists():
        return None
    else:
        settings = argconvert.convert_arg_list(border_removal.args.list)
        j = Job(job_name=JOB_NAME,
                author="Deepanjan Roy",
                description="Automatically tries to remove the border of a page. Non-interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [1], "name": "greyscale"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [1], "name": "greyscale"},
                settings=settings,
                enabled=True,
                category="Border Removal",
                interactive=False
                )

        j.save()
