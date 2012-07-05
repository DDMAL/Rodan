from celery.task import task

import utils

from rodan.models.projects import Page


@task
def create_thumbnails_task(page_id, image_path, thumbnail_sizes):
    page = Page.objects.get(pk=page_id)
    for thumbnail_size in thumbnail_sizes:
        thumb_path = page.get_thumb_path(size=thumbnail_size)
        utils.create_thumbnail(image_path, thumb_path, thumbnail_size)
