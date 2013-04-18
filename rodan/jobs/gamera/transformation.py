from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.plugins import transformation


def load_module():
    create_jobs_from_module(transformation)
