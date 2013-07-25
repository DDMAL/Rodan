from celery import task
from rodan.helpers.dbmanagement import refetch_from_db, exists_in_db


@task(name="rodan.helpers.processed")
def processed(dbobject):
    dbobject = refetch_from_db(dbobject)
    dbobject.processed = True
    if exists_in_db(dbobject):
        dbobject.save()
    return dbobject
