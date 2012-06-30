import utils
import gamera.core

from django.conf import settings
from django.conf.urls import patterns, url

from rodan.models.jobs import JobType, JobBase

neon_urls = patterns('rodan.views.neon',
    url(r'^insert/neume', 'insert_neume'),
    url(r'^move/neume', 'move_neume'),
    url(r'^delete/neume', 'delete_neume'),
    url(r'^neumify', 'neumify'),
    url(r'^ungroup', 'ungroup'),
    url(r'^insert/division', 'insert_division'),
    url(r'^move/division', 'move_division'),
    url(r'^delete/division', 'delete_division'),
    url(r'^insert/dot', 'insert_dot'),
    url(r'^delete/dot', 'delete_dot'),
    url(r'^insert/clef', 'insert_clef'),
    url(r'^move/clef', 'move_clef'),
    url(r'^update/clef/shape', 'update_clef_shape'),
    url(r'^delete/clef', 'delete_clef'),
    url(r'^insert/custos', 'insert_custos'),
    url(r'^move/custos', 'move_custos'),
    url(r'^delete/custos', 'delete_custos')
)

@utils.rodan_task(inputs=None)
def neon(image_filepath, **kwargs):
    return {
        'mei': ''
    }

class Neon(JobBase):
    name = 'Neon'
    slug = 'neon'
    input_type = JobType.MEI
    output_type = JobType.MEI
    description = 'Correct OMR errors.'
    show_during_wf_create = False
    parameters = {
        'data': ''
    }
    task = neon
    outputs_image = False

    def get_context(self, page):
        latest_image_path = page.get_latest_file_path('tiff')
        image = gamera.core.load_image(latest_image_path)
        return {
            'bgimgpath': page.get_pre_bin_image_url(),
            'orig_width': image.size.width,
            'page_id': page.id,
            'mei_path': page.get_mei_url()
        }

