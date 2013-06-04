from rodan.models.job import Job
from rodan.jobs.gamera.custom.segmentation.celery_task import JOB_NAME
from rodan.jobs.gamera import argconvert
from rodan.settings import ONEBIT


def load_segmentation():
    job = Job.objects.filter(job_name=JOB_NAME)
    if job.exists():
        return None
    else:
        settings = [{'default':0,'has_default':True,'rng':(-1048576,1048576),'name':'num lines','type':'int'},
                    {'default':5,'has_default':True,'rng':(-1048576,1048576),'name':'scanlines','type':'int'},
                    {'default':0.8,'has_default':True,'rng':(-1048576,1048576),'name':'blackness','type':'real'},
                    {'default':-1,'has_default':True,'rng':(-1048576,1048576),'name':'tolerance','type':'int'},
                    {'default': None,'has_default':True,'name':'polygon_outer_points','type':'json'},
                    {'default': 0,'has_default':True,'rng':(-1048576,1048576),'name':'image_width','type':'int'}]

        j = Job(job_name=JOB_NAME,
                author="Deepanjan Roy",
                description="Finds the staves using Miyao Staff Finder and masks out everything else.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [ONEBIT,], "name": "output"},
                settings=settings,
                enabled=True,
                category="Segmentation",
                interactive=True
                )

        j.save()


def load_module():
    load_segmentation()
