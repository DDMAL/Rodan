from djcelery_transactions import task
from rodan.jobs.utils import create_thumbnail
from rodan.models.projects import Page


@task
def create_thumbnails(page_id, image_path, thumbnail_sizes):
    """
    Celery task for creating thumbnails immediately after uploading an image.
    """
    Page = models.get_model('rodan', 'Page')
    page = Page.objects.select_for_update().get(pk=page_id)
    for thumbnail_size in thumbnail_sizes:
        thumb_path = page.get_thumb_path(size=thumbnail_size)
        width, height = create_thumbnail(image_path, thumb_path, thumbnail_size)

    # Save the dimensions (in original AND latest, since jobs use latest)
    page.original_width = width
    page.latest_width = width
    page.original_height = height
    page.latest_height = height

    page.is_ready = True
    page.save()
