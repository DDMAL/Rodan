"""
Startup Rodan database.
Called by urls.py as suggested by http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
"""
import sys
from rodan.models import ResourceType

TEST = 'test' in sys.argv

def startup():
    load_resource_type()


def load_resource_type():
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
