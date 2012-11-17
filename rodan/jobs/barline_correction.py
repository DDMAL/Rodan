import os
from django.conf import settings
from rodan.jobs.utils import rodan_task, create_dirs
from rodan.models.jobs import JobType, JobBase
from rodan.models.projects import Job


@rodan_task(inputs=[])
def barline_correction(**kwargs):
    return {
    }


class BarlineCorrection(JobBase):
    name = 'Barline Correction'
    slug = 'barline-correction'
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
        create_dirs(output_path)
        if not os.path.exists(output_path):
            f = open(output_path, 'w')
            f.write(open(input_mei_path).read())
            f.close()

        mei_url = settings.MEDIA_URL + page._get_job_path(j, 'mei')
        return {
            'bgimgpath': page.get_latest_thumb_url(settings.LARGE_THUMBNAIL),
            'scaled_width': settings.LARGE_THUMBNAIL,
            'orig_width': page.latest_width,
            'orig_height': page.latest_height,
            'page_id': page.id,
            'mei_path': mei_url
        }
