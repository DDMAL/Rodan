from rodan.jobs.gamera.helpers import create_jobs_from_module
from gamera.toolkits.lyric_extraction.plugins import border_lyric
from gamera.toolkits.lyric_extraction.plugins import lyricline


def load_module():
    create_jobs_from_module(border_lyric)
    create_jobs_from_module(lyricline)
