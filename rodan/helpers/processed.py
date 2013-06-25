from celery import task


@task(name="rodan.helpers.processed")
def processed(dbobject):
    dbobject.processed = True
    dbobject.save()
    return dbobject
