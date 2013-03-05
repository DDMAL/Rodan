from rodan.jobs.helpers import create_interactive_job_from_gamera_function
from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop


def load_interactive_job():
    create_interactive_job_from_gamera_function(rdn_crop)
