"""
Startup Rodan database.
Called by urls.py as suggested by http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
"""
import sys
from rodan.models import ResourceType

TEST = 'test' in sys.argv

def startup():
    load_resource_types()
    if TEST:
        import rodan.jobs     # just test if they are defined correctly and make no errors. Jobs are initialized by Celery thread.
        import rodan.test.dummy_jobs
        reload(rodan.test.dummy_jobs)

def load_resource_types():
    load = ResourceType.load  # short-hand

    load('application/octet-stream', 'Unknown type', '')  # RFC 2046
    load('image/onebit+png', '', 'png')
    load('image/greyscale+png', '', 'png')
    load('image/grey16+png', '', 'png')
    load('image/rgb+png', '', 'png')
    load('image/float+png', '', 'png')
    load('image/complex+png', '', 'png')
    load('application/mei+xml', '', 'mei')
    load('image/jp2', 'jpeg2000', 'jp2')  # RFC 3745
    load('application/zip', 'Package', 'zip')
    load('application/gamera+xml', 'Gamera classifier XML', 'xml')

    if TEST:
        load('test/a1', '')
        load('test/a2', '')
        load('test/b', '')
