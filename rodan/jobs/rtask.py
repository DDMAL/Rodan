import djcelery_transactions

from djcelery.models import TaskMeta
from rodan.models.results import Result, ResultTask


class RTask(djcelery_transactions.Task):

    def after_return(self, status, retval, task_id, args, kwargs, einfo=None):
        '''
        This function overides the default behaviour of after_return() of a celery task (i.e @task)
        to link Result objects to TaskMeta object via ResultTask. The main reason for this is to decouple
        tasks that fail by exception from the monitoring process. This will also account for tasks that
        succeed as well.
        Note that this will not catch python crashes - the monitor needs to be running to catch them and
        link them properly to the Result object.
        '''
        t = TaskMeta.objects.get(task_id=task_id)

        result_id = args[0]
        result = Result.objects.select_for_update().get(pk=result_id)
        result.task_state = t.status
        result.save()
        rtask, created = ResultTask.objects.get_or_create(result=result, task=t)


class RTaskMultiPage(djcelery_transactions.Task):

    def after_return(self, status, retval, task_id, args, kwargs, einfo=None):
        '''
        This function overides the default behaviour of after_return() of a celery task (i.e @task)
        to link Result objects to TaskMeta object via ResultTask. The main reason for this is to decouple
        tasks that fail by exception from the monitoring process. This will also account for tasks that
        succeed as well.
        Note that this will not catch python crashes - the monitor needs to be running to catch them and
        link them properly to the Result object.
        '''
        t = TaskMeta.objects.get(task_id=task_id)

        # link all the results to the same TaskMeta record
        for result_id in args[0]:
            result = Result.objects.select_for_update().get(pk=result_id)
            result.task_state = t.status
            result.save()
            rtask, created = ResultTask.objects.get_or_create(result=result, task=t)
