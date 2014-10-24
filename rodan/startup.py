"""
Startup Rodan database.
Called by urls.py as suggested by http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
"""
import sys
from rodan.models import ResourceType
from rodan.jobs import load_jobs as load_rodan_jobs

TEST = 'test' in sys.argv

def startup():
    load_resource_types()
    load_jobs()


def load_resource_types():
    load_type('application/octet-stream', 'Unknown type')  # RFC 2046
    load_type('image/onebit+png', '')
    load_type('image/greyscale+png', '')
    load_type('image/grey16+png', '')
    load_type('image/rgb+png', '')
    load_type('image/float+png', '')
    load_type('image/complex+png', '')
    load_type('application/mei+xml', '')
    load_type('image/jp2', 'jpeg2000')  # RFC 3745
    load_type('application/zip', 'Package')
    load_type('application/gamera+xml', 'Gamera classifier XML')

    if TEST:
        load_type('test/a1', '')
        load_type('test/a2', '')
        load_type('test/b', '')

def load_type(mimetype, description):
    if not ResourceType.objects.filter(mimetype=mimetype).exists():
        ResourceType(mimetype=mimetype, description=description).save()

def load_jobs():
    load_rodan_jobs()
    if TEST:
        from rodan.jobs.devel.dummy_job import load_dummy_automatic_job, load_dummy_manual_job
        load_dummy_automatic_job()
        load_dummy_manual_job()
