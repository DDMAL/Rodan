from celery.task import task

import utils


@task
def create_thumbnails_task(page, image_path, thumbnail_sizes):
    for thumbnail_size in thumbnail_sizes:
        thumb_path = page.get_thumb_path(size=thumbnail_size)
        utils.create_thumbnail(image_path, thumb_path, thumbnail_size)
