from rodan.jobs.utils import rodan_task
from rodan.models.jobs import JobType, JobBase


@rodan_task(inputs='prebin')
def diva(image_filepath, **kwargs):
    compression = kwargs['compression']
    quality = kwargs['quality']
    tile_size = kwargs['tile_size']

    if compression == 'jpeg':
        # For JPEG compression, we have to use the quality as well
        compression = "{0}:{1}".format(compression, quality)

    return {
        'vips': (image_filepath, compression, tile_size)
    }


class Diva(JobBase):
    name = 'Diva preprocessing'
    slug = 'diva-preprocess'
    input_type = JobType.SOLR
    output_type = JobType.END
    description = 'Prepare an image to be shown in the image viewer.'
    show_during_wf_create = False
    enabled = False
    parameters = {
        'quality': 75,
        'tile_size': 256,
        'compression': 'jpeg'
    }
    task = diva
    outputs_image = False
    is_automatic = True
