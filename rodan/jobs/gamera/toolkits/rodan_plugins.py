from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.toolkits.rodan_plugins.plugins.rdn_rotate import rdn_rotate
from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop


def load_module():
    create_jobs_from_module(rdn_rotate, interactive=True)
    create_jobs_from_module(rdn_despeckle, interactive=True)
    create_jobs_from_module(rdn_despeckle, interactive=False)
    create_jobs_from_module(rdn_crop, interactive=True)
