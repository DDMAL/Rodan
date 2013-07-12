import os
import json
from functools import wraps
from django.http.response import HttpResponse
from rodan.settings import PROJECT_DIR


def render_to_json(**jsonargs):
    """
    Renders a JSON response with a given returned instance. Assumes json.dumps() can
    handle the result. The default output uses an indent of 4.

    @render_to_json()
    def a_view(request, arg1, argN):
        ...
        return {'x': range(4)}

    @render_to_json(indent=2)
    def a_view2(request):
        ...
        return [1, 2, 3]

    From http://djangosnippets.org/snippets/2102/
    """
    def outer(f):
        @wraps(f)
        def inner_json(request, *args, **kwargs):
            result = f(request, *args, **kwargs)
            r = HttpResponse(mimetype='application/json')
            indent = jsonargs.pop('indent', 4)
            r.write(json.dumps(result, indent=indent, **jsonargs))
            return r
        return inner_json
    return outer

neon_backup_directory = 'backup_neon'
live_mei_filename = 'live_edit.mei'
backup_mei_filename = 'backup_mei.mei'
compressed_image_name = 'neon_compressed.jpg'


def live_mei_directory(runjob):
    return os.path.join(runjob.runjob_path, neon_backup_directory)


def live_mei_path(runjob):
    return os.path.join(live_mei_directory(runjob), live_mei_filename)


def live_mei_url(runjob):
    runjob_rel_path = os.path.relpath(runjob.runjob_path, PROJECT_DIR)
    return os.path.join(runjob_rel_path, neon_backup_directory, live_mei_filename)


def backup_mei_path(runjob):
    return os.path.join(live_mei_directory(runjob), backup_mei_filename)


def compressed_image_path(runjob):
    return os.path.join(live_mei_directory(runjob), compressed_image_name)


def compressed_image_url(runjob):
    runjob_rel_path = os.path.relpath(runjob.runjob_path, PROJECT_DIR)
    return os.path.join(runjob_rel_path, neon_backup_directory, compressed_image_name)
