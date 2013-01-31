from rodan.jobs.interactive.helpers import create_interactive_job_from_gamera_function
from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle


def load_interactive_job():
    create_interactive_job_from_gamera_function(rdn_despeckle)
