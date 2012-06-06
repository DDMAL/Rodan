from rodan.models.jobs import JobType, JobBase
from tasks import tasks 

class RankFilter(JobBase):
    name = 'Rank filter'
    slug = 'rank-filter'
    input_type = JobType.IMAGE_GREY
    output_type = input_type
    description = 'Applies rank filter on a binarized image'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        rank_val = kwargs['rank_val']
        k = kwargs['k']
        border_treatment = kwargs['border_treatment']
        tasks.rank_filter.delay(result_id,rank_val,k,border_treatment)
