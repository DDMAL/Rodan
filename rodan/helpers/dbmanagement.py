from rodan.helpers.exceptions import ObjectDeletedError
import urlparse
from django.core.urlresolvers import resolve


def exists_in_db(dbobject):
    if dbobject.uuid and type(dbobject).objects.filter(pk=dbobject.uuid).exists():
        return True
    else:
        return False


def refetch_from_db(dbobject):
    try:
        return type(dbobject).objects.get(pk=dbobject.uuid)
    except type(dbobject).DoesNotExist:
        raise ObjectDeletedError("Object could not be refetched: The object no longer exists in the database.")


def resolve_object_from_url(model_class, url):
    """Arguments:
           model_class: A django model class. Import the class and pass it in.
           url: The url that you're trying to resolve.

       Returns the resolved model instance.

       Raises Resolver404 if no view is found that handles the given url.

       Raises model_class.DoesNotExist if the database record with the supplied
       primary key does not exist.
    """
    url_path = urlparse.urlparse(url).path
    object_view = resolve(url_path)
    return model_class.objects.get(pk=object_view.kwargs['pk'])
