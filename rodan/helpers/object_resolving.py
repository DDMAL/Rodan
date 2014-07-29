import urlparse
from django.core.urlresolvers import resolve


def resolve_to_object(request_url, model):
    """
        Arguments:
           model: A django model class. Import the class and pass it in.
           request_url: The url that you're trying to resolve.

       Returns the resolved model instance.

       Raises Resolver404 if no view is found that handles the given url.

       Raises AttributeError if no request_url is None.

       Raises model.DoesNotExist if the database record with the supplied
       primary key does not exist.
    """
    value = urlparse.urlparse(request_url).path
    o = resolve(value)
    obj_pk = o.kwargs.get('pk')
    return model.objects.get(pk=obj_pk)
