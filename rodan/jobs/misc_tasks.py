from celery.task import task

import utils

from rodan.models.projects import Page


@task
def create_thumbnails_task(page_id, image_path, thumbnail_sizes):
    """
    Celery task for creating thumbnails immediately after uploading an image.
    """
    page = Page.objects.select_for_update().get(pk=page_id)
    for thumbnail_size in thumbnail_sizes:
        thumb_path = page.get_thumb_path(size=thumbnail_size)
        width, height = utils.create_thumbnail(image_path, thumb_path, thumbnail_size)

    # Save the dimensions (in original AND latest, since jobs use latest)
    page.original_width = width
    page.latest_width = width
    page.original_height = height
    page.latest_height = height

    page.is_ready = True
    page.save()
