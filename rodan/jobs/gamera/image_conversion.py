from rodan.jobs.gamera.helpers import create_jobs_from_module
from gamera.plugins import image_conversion


def load_module():
    create_jobs_from_module(image_conversion)
