from celery import task


@task(name="rodan.helpers.pagedone.pagedone")
def pagedone(page_object):
    page_object.processed = True
    page_object.save()
    return page_object
