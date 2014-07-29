from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.toolkits.musicstaves.plugins import musicstaves_plugins


def load_module():
    create_jobs_from_module(musicstaves_plugins)
