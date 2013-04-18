from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.toolkits.background_estimation.plugins import background_estimation


def load_module():
    create_jobs_from_module(background_estimation)
