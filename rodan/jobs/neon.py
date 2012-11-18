import os

from django.conf import settings
from django.conf.urls import patterns, url
from rodan.helpers.filesystem import create_dirs

from rodan.jobs.utils import rodan_task
from rodan.celery_models.jobtype import JobType
from rodan.celery_models.jobbase import JobBase

from rodan.models.job import Job

neon_urls = patterns('rodan.views.neon',
    url(r'^insert/neume', 'insert_neume'),
    url(r'^move/neume', 'move_neume'),
    url(r'^delete/neume', 'delete_neume'),
    url(r'^update/neume/headshape', 'update_neume_head_shape'),
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


@rodan_task(inputs=[])
def neon(**kwargs):
    return {
    }


class Neon(JobBase):
    name = 'Neon'
    slug = 'neon'
    input_type = JobType.MEI
    output_type = JobType.MEI
    description = 'Correct recognition errors.'
    show_during_wf_create = False
    enabled = False
    parameters = {
        'data': ''
    }
    task = neon
    outputs_image = False

    def get_context(self, page):
        input_mei_path = page.get_latest_file_path('mei')

        j = Job.objects.get(pk=self.slug)
        output_path = page.get_job_path(j, 'mei')
        create_dirs(output_path)
        if not os.path.exists(output_path):
            f = open(output_path, 'w')
            f.write(open(input_mei_path).read())
            f.close()

        mei_url = settings.MEDIA_URL + page._get_job_path(j, 'mei')
        return {
            'bgimgpath': page.get_pre_bin_image_url(),
            'scaled_width': settings.LARGE_THUMBNAIL,
            'orig_width': page.latest_width,
            'orig_height': page.latest_height,
            'page_id': page.id,
            'mei_path': mei_url
        }
