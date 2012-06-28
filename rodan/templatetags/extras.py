from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_range(end, start=1):
    """
    Filter - returns a list containing range made from given value

    """
    return range(start, end + 1)

@register.simple_tag
def get_thumb_for_job(page, job=None, size=settings.SMALL_THUMBNAIL):
    return page.get_thumb_url(job=job, size=size)

@register.filter
def is_job_complete(page, job_item):
    return page.is_job_complete(job_item)

@register.simple_tag
def progress_bar(percentage):
    if percentage < 10:
        colour = 'none'
    elif percentage < 20:
        colour = 'red'
    elif percentage < 30:
        colour = 'orange'
    elif percentage < 40:
        colour = 'yellow'
    else:
        colour = 'green'

    return '<div class="progress"><div class="bar %s" style="width: %d%%;">%d%%</div></div>' % (colour, percentage, percentage)
