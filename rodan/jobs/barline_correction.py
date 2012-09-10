import utils

import os

from django.conf import settings

from rodan.models.jobs import JobType, JobBase
from rodan.models.projects import Job

@utils.rodan_task(inputs=[])
def barline_correction(**kwargs):
    return {
    }

class BarlineCorrection(JobBase):
    name = 'Barline Correction'
    slug = 'barline_correction'
    input_type = JobType.MEI
    output_type = JobType.CORRECTED_MEI
    description = 'Correct barline detection errors.'
    show_during_wf_create = True
    parameters = {
        'data': ''
    }
    task = barline_correction
    outputs_image = False

    def get_context(self, page):
        input_mei_path = page.get_latest_file_path('mei')

        j = Job.objects.get(pk=self.slug)
        output_path = page.get_job_path(j, 'mei')
        utils.create_dirs(output_path)
        if not os.path.exists(output_path):
            open(output_path, 'w').write(open(input_mei_path).read())

        mei_url = settings.MEDIA_URL + page._get_job_path(j, 'mei')
        return {
            'bgimgpath': page.get_pre_bin_image_url(),
            'scaled_width': settings.LARGE_THUMBNAIL,
            'orig_width': page.latest_width,
            'orig_height': page.latest_height,
            'page_id': page.id,
            'mei_path': mei_url
        }
