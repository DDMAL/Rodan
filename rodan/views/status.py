from django.shortcuts import get_object_or_404

from rodan.utils import render_to_json
from rodan.models.results import Result
from rodan.models.projects import Page


@render_to_json()
def task(request):
    '''
    The following will set:
        -1 to a task that has failed
        1 to a task that has finished executing
        0 to a task that hasn't finished executing
    '''
    result_ids = request.GET.getlist('result_ids[]')
    result_statuses = {}

    for result_id in result_ids:
        try:
            result = Result.objects.get(pk=result_id)
            result_taskstate = result.task_state
            if result_taskstate is not None and result_taskstate.state == "FAILURE":
                result_statuses[result_id] = -1
            elif result.end_total_time is not None:
                result_statuses[result_id] = 1
            else:
                result_statuses[result_id] = 0
        except Result.DoesNotExist:
            pass

    return result_statuses


@render_to_json()
def page(request, page_id):
    return get_object_or_404(Page, pk=page_id).is_ready
