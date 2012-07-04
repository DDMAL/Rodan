from celery.task import task

import utils


@task
def create_thumbnails_task(image_path, thumb_path, thumbnail_size):
    utils.create_thumbnail(image_path, thumb_path, thumbnail_size)
