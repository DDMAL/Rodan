from rodan.celery import app
import yaml
from yaml.loader import SafeLoader

import os
import environ
import importlib
"""
Script for registering Rodan jobs with Celery, split into their respective queues
"""
ROOT_DIR = environ.Path(__file__) - 2
PROJECT_PATH = ROOT_DIR.path("rodan")

# Open the file and load the file
with open(os.path.join(os.path.dirname(PROJECT_PATH), 'registerJobs.yaml')) as file:
    allJobs = yaml.load(file, Loader=SafeLoader)

# Register all jobs
def register_all():
    # Register all jobs
    register_base()
    register_py3()
    register_gpu()


# base jobs
def register_base():

    for path in allJobs['BASE_JOB_PACKAGES']:
        for base_job in allJobs['BASE_JOB_PACKAGES'][path]:
            try: 
                # from path import base_job as job_name
                job_class = getattr(importlib.import_module(path), base_job)                
                app.register_task(job_class)

            except Exception as exception:
                print(base_job + " failed to import with the following error:",  exception.__class__.__name__)

# Python3 Jobs
def register_py3():
    for pack in allJobs['RODAN_PYTHON3_JOBS']:
        for path in allJobs['RODAN_PYTHON3_JOBS'][pack]:
            for py3_job in allJobs['RODAN_PYTHON3_JOBS'][pack][path]:
                try: 
                    #from path import py3_job as job_name
                    job_class = getattr(importlib.import_module(path), py3_job)  
                    app.register_task(job_class)

                except Exception as exception:
                    print(py3_job + " failed to import with the following error:",  exception.__class__.__name__)


def register_gpu():
    for pack in allJobs["RODAN_GPU_JOBS"]:
        for path in allJobs["RODAN_GPU_JOBS"][pack]:
            for gpu_job in allJobs["RODAN_GPU_JOBS"][pack][path]:
                try: 
                    #from path import py3_job as job_name
                    job_class = getattr(importlib.import_module(path), gpu_job)  
                    app.register_task(job_class)

                except Exception as exception:
                    print(gpu_job + " failed to import with the following error:",  exception.__class__.__name__)

if __name__ == "__main__":
    register_all()
