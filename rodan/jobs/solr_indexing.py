import gamera.core
from django.conf import settings

import utils
import solr_resources.MEI2Solr
from rodan.models.jobs import JobType, JobBase

gamera.core.init_gamera()


@utils.rodan_task(inputs='mei')
def index_solr(mei_filepath, **kwargs):
    solr_resources.MEI2Solr.processMeiFile(mei_filepath, settings.SOLR_URL,\
        kwargs['longest_gram'], kwargs['shortest_gram'])

    return {
    }


class SolrIndexing(JobBase):
    name = 'Solr indexing'
    slug = 'solr-indexing'
    input_type = JobType.MEI
    output_type = JobType.SOLR
    description = 'Indexes .mei data into SOLR'
    show_during_wf_create = True
    parameters = {
        'shortest_gram': 2,
        'longest_gram': 9,
    }
    task = index_solr
    is_automatic = True
    outputs_image = False
