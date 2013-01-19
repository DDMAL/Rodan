from django.shortcuts import get_object_or_404

from rodan.utils import render_to_json
from rodan.models.result import Result
from rodan.models.page import Page


@render_to_json()
def task(request):
    '''
    The following will set:
        -1 to a task that has failed
        1 to a task that has finished executing
        0 to a task that hasn't finished executing
    '''
    result_ids = request.GET.getlist('result_ids[]')
    results = Result.objects.filter(pk__in=result_ids)
    result_statuses = {}

    for result in results:
        result_taskstate = result.task_state
        if result_taskstate is not None and result_taskstate == "FAILURE":
            result_statuses[result.id] = -1
        elif result.end_total_time is not None:
            result_statuses[result.id] = 1
        else:
            result_statuses[result.id] = 0

    return result_statuses


@render_to_json()
def page(request, page_id):
    return get_object_or_404(Page, pk=page_id).is_ready
