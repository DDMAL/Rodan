from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.toolkits.staffline_removal.plugins import staff_removal


def load_module():
    create_jobs_from_module(staff_removal)
