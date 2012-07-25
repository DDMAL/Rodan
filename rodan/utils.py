import os
from functools import wraps

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils import simplejson as json


def remove_prefixes(s):
    """Removes everything before the last .

    So jobs.rotation.Rotate would become Rotate.

    Preserves case.
    """
    return s[s.rfind('.') + 1:]


def headers(**h):
    """Decorator adding arbitrary HTTP headers to the response.

    This decorator adds HTTP headers specified in the argument (map), to the
    HTTPResponse returned by the function being decorated. If the header that
    you are inserting contains a '-' character, replace it with underscores when
    applying the decorator (i.e Cache-Control should be written as Cache_Control).

    Example:

    @headers(Cache_Control='no-cache, no-store, max-age=0, must-revalidate', Expires='Fri, 01 Jan 2010 00:00:00 GMT')
    def index(request):
        ....
    """
    def headers_wrapper(f):
        def wrapped_function(*args, **kwargs):
            response = f(*args, **kwargs)
            for k, v in h.iteritems():
                response[k.replace('_', '-')] = v
            return response
        return wrapped_function
    return headers_wrapper


def rodan_view(*models):
    def outer_function(f):
        def inner_function(request, **kwargs):
            model_instances = []

            for model in models:
                pk = kwargs[model.pk_name]
                del kwargs[model.pk_name]
                model_instance = get_object_or_404(model, pk=pk)
                model_instances.append(model_instance)

            output = f(request, *model_instances, **kwargs)

            try:
                breadcrumbs = []
                model = model_instances[0]
                while hasattr(model, "get_parent"):
                    breadcrumbs.append(model)
                    model = model.get_parent()

                breadcrumbs.append(model)

                title, context = output

                dir_name = f.__module__
                # Get rid of everything before the last .
                dir_name = dir_name[dir_name.rindex('.') + 1:]
                template_name = f.__name__
                template_file = os.path.join(dir_name, template_name + '.html')

                context['title'] = title
                context['model'] = model_instance
                context['template_file'] = template_file
                context['breadcrumbs'] = reversed(breadcrumbs)

                for model_instance in model_instances:
                    model_name = model_instance.__class__.__name__.lower()
                    context[model_name] = model_instance

                return render(request, 'detail.html', context)
            except ValueError:
                return output

        return inner_function
    return outer_function


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


def chunkify(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def get_size_in_mb(num_bytes):
    return "%.2fMB" % (num_bytes / 1000000.0)
