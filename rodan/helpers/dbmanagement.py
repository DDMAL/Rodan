from rodan.helpers.exceptions import ObjectDeletedError


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
