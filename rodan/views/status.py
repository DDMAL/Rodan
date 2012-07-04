from rodan.utils import render_to_json
from rodan.models.results import Result


@render_to_json()
def task(request):
    result_ids = request.GET.getlist('result_ids[]')
    result_statuses = {}

    for result_id in result_ids:
        try:
            result = Result.objects.get(pk=result_id)
            is_done = result.end_total_time is not None
            result_statuses[result_id] = is_done
        except Result.DoesNotExist:
            pass

    return result_statuses
