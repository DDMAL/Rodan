import urlparse
from django.core.urlresolvers import resolve


def resolve_to_object(request_url, model):
    value = urlparse.urlparse(request_url).path
    o = resolve(value)
    obj_pk = o.kwargs.get('pk')
    return model.objects.get(pk=obj_pk)
