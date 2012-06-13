import gamera.core
from gamera.plugins.morphology import despeckle

import utils
from rodan.models.jobs import JobType, JobBase


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


class Despeckle(JobBase):
    name = 'Despeckle'
    slug = 'despeckle'
    input_type = JobType.BINARISED_IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Despeckle a binarized image'
    show_during_wf_create = True
    parameters = {
        'despeckle_value': 100
    }
    task = despeckle
