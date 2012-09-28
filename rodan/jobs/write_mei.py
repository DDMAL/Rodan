import utils
from rodan.models.jobs import JobType, MultiPageJobBase

from mei_resources.meicombine import MeiCombiner


@utils.rodan_multi_page_task(inputs='mei')
def combine_mei(mei_paths, **kwargs):
    mc = MeiCombiner(mei_paths)
    mc.combine()
    combined_mei = mc.get_mei()

    return {
        'mei': combined_mei,
    }


class CombineMei(MultiPageJobBase):
    name = 'Combine all MEI files'
    slug = 'combine-mei'
    input_type = JobType.CORRECTED_MEI
    output_type = JobType.END
    description = 'Make a single MEI file out of all images'
    show_during_wf_create = True
    is_automatic = True
    outputs_image = False
    task = combine_mei
