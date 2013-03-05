from rodan.jobs.helpers import create_jobs_from_module
from gamera.toolkits.border_removal.plugins import border_removal


def load_module():
    create_jobs_from_module(border_removal)
