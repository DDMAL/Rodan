import gamera.core

import utils
from rodan.models.jobs import JobType, JobBase

gamera.core.init_gamera()


@utils.rodan_task(inputs='tiff')
def despeckle(image_filepath, **kwargs):
    """
      Removes connected components that are smaller than the given size.

      *size*
        The maximum number of pixels in each connected component that
        will be removed.

      This approach to finding connected components uses a pseudo-recursive
      descent, which gets around the hard limit of ~64k connected components
      per page in ``cc_analysis``.  Unfortunately, this approach is much
      slower as the connected components get large, so *size* should be
      kept relatively small.

      *size* == 1 is a special case and runs much faster, since it does not
      require recursion.
    """
    # must be OneBit, not using rodan load image (although it does prevent conversion to one bit)
    input_image = gamera.core.load_image(image_filepath)
    input_image.despeckle(kwargs['despeckle_value'])

    return {
        'tiff': input_image
    }

class PostStaffRemovalDespeckle(JobBase):
    name = 'Despeckle after staff removal'
    slug = 'despeckle-staff'
    input_type = JobType.NEUME_IMAGE
    output_type = JobType.NEUME_DESPECKLE_IMAGE
    description = "Despeckle an image that's had its stafflines removed."
    show_during_wf_create = True
    is_automatic = True
    parameters = {
        'despeckle_value': 100
    }
    task = despeckle

    def get_context(self, page):
        return {
            'width': page.latest_width,
        }

class Despeckle(JobBase):
    name = 'Despeckle'
    slug = 'despeckle'
    input_type = JobType.BINARISED_IMAGE
    output_type = JobType.DESPECKLE_IMAGE
    description = 'Despeckle a binarised image.'
    show_during_wf_create = True
    is_automatic = True
    parameters = {
        'despeckle_value': 100
    }
    task = despeckle

    def get_context(self, page):
        return {
            'width': page.latest_width,
        }
