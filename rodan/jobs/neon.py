import utils

from django.conf import settings
from django.conf.urls import patterns, url

from rodan.models.jobs import JobType, JobBase

neon_urls = patterns('rodan.views.neon',
    url(r'^edit/insert/neume', 'insert_neume'),
    url(r'^edit/move/neume', 'move_neume'),
    url(r'^edit/delete/neume', 'delete_neume'),
    url(r'^edit/neumify', 'neumify'),
    url(r'^edit/ungroup', 'ungroup'),
    url(r'^edit/insert/division', 'insert_division'),
    url(r'^edit/move/division', 'move_division'),
    url(r'^edit/delete/division', 'delete_division'),
    url(r'^edit/insert/dot', 'insert_dot'),
    url(r'^edit/delete/dot', 'delete_dot'),
    url(r'^edit/insert/clef', 'insert_clef'),
    url(r'^edit/move/clef', 'move_clef'),
    url(r'^edit/update/clef/shape', 'update_clef_shape'),
    url(r'^edit/delete/clef', 'delete_clef'),
    url(r'^edit/insert/custos', 'insert_custos'),
    url(r'^edit/move/custos', 'move_custos'),
    url(r'^edit/delete/custos', 'delete_custos')
)

@utils.rodan_task(inputs=None)
def neon(image_filepath, **kwargs):
    return {
        'mei': ''
    }

class Neon(JobBase):
    name = 'Neon'
    slug = 'neon'
    input_type = JobType.MEI_UNCORRECTED
    output_type = JobType.MEI_CORRECTED
    description = 'Correct OMR errors.'
    show_during_wf_create = False
    parameters = {
        'data': ''
    }
    task = neon
    outputs_image = False

    def get_context(self, page):
        return {
            'image': page.get_pre_bin_image_url(),
        }
