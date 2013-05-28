from rodan.models.job import Job
from rodan.jobs.gamera.custom.border_removal.celery_task import JOB_NAME_AUTO, JOB_NAME_CROP_BR
from rodan.jobs.gamera import argconvert
from gamera.toolkits.border_removal.plugins.border_removal import border_removal
from rodan.settings import ONEBIT, GREYSCALE, RGB


def load_auto_border_removal():
    job = Job.objects.filter(job_name=JOB_NAME_AUTO)
    if job.exists():
        return None
    else:
        settings = argconvert.convert_arg_list(border_removal.args.list)
        j = Job(job_name=JOB_NAME_AUTO,
                author="Deepanjan Roy",
                description="Automatically tries to remove the border of a page. Non-interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "output"},
                settings=settings,
                enabled=True,
                category="Border Removal",
                interactive=False
                )

        j.save()


def load_crop_border_removal():
    job = Job.objects.filter(job_name=JOB_NAME_CROP_BR)
    if job.exists():
        return None
    else:
        from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
        settings = argconvert.convert_arg_list(rdn_crop.args.list)
        j = Job(job_name=JOB_NAME_CROP_BR,
                author="Deepanjan Roy",
                description="Manual masking crop. Uses the crop interface. Interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "output"},
                settings=settings,
                enabled=True,
                category="Border Removal",
                interactive=True
                )

        j.save()    


def load_module():
    load_auto_border_removal()
    load_crop_border_removal()