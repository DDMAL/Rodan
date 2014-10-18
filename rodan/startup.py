"""
Registers ResourceTypes into Rodan database.
Called by urls.py as suggested by http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
"""
import sys
from rodan.models import ResourceType

TEST = 'test' in sys.argv

def startup():
    load_resource_type()


def load_resource_type():
    load_type('onebit', '')
    load_type('greyscale', '')
    load_type('grey16', '')
    load_type('rgb', '')
    load_type('float', '')
    load_type('complex', '')
    load_type('mei', '')
    load_type('jpeg2000', '')
    load_type('package', '')
    load_type('gamera_xml', '')
    load_type('image', '')
    load_type('png', '')
    load_type('bmp', '')
    load_type('jpeg', '')
    load_type('xml', '')

    if TEST:
        load_type('test_type', '')
        load_type('test_type2', '')
        load_type('test_type3', '')

def load_type(name, description):
    if not ResourceType.objects.filter(name=name).exists():
        ResourceType(name=name, description=description).save()
