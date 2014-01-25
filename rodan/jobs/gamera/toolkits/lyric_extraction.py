from rodan.jobs.gamera.module_loader import create_jobs_from_module
from gamera.toolkits.lyric_extraction.plugins import border_lyric
from gamera.toolkits.lyric_extraction.plugins import lyricline
from gamera.toolkits.lyric_extraction.plugins import lyric_extractor


def load_module():
    create_jobs_from_module(border_lyric)
    create_jobs_from_module(lyricline)
    create_jobs_from_module(lyric_extractor)
