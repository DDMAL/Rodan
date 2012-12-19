from django.conf import settings
from rodan.jobs.utils import rodan_task
from rodan.jobs.solr_resources import MEI2Solr
from rodan.celery_models.jobtype import JobType
from rodan.celery_models.jobbase import JobBase


@rodan_task(inputs=('mei'), others=['page_sequence', 'project_id'])
def index_solr(mei_filepath, page_number, project_id, **kwargs):
    print page_number
    MEI2Solr.processMeiFile(mei_filepath, settings.SOLR_URL,\
        kwargs['shortest_gram'], kwargs['longest_gram'], page_number, project_id)
    return {}


class SolrIndexing(JobBase):
    name = 'Solr indexing'
    slug = 'solr-indexing'
    input_type = JobType.MEI
    output_type = JobType.SOLR
    description = 'Index an MEI file into the search database.'
    show_during_wf_create = True
    enabled = False
    parameters = {
        'shortest_gram': 2,
        'longest_gram': 9,
    }
    task = index_solr
    is_automatic = True
    outputs_image = False
