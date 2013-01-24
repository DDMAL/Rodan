from rodan.jobs.interactive.helpers import create_interactive_job_from_gamera_function
from gamera.plugins.morphology import despeckle


def load_interactive_job():
    create_interactive_job_from_gamera_function(despeckle)
