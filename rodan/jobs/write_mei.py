import utils
from rodan.models.jobs import JobType, JobBase
from rodan.models import Page
from pymei import XmlImport

from mei_resources.meicombine import MeiCombiner

@utils.rodan_multi_task(inputs='mei')
def combine_mei(mei_path, **kwargs):
    target_page_ids = kwargs['target_page_ids']

    # the first element of the list is the page that's sending the job
    # and the rest of the list are all other pages waiting to get merged
    mei_paths = [str(mei_path)]

    # get the meis of all other pages
    for page_id in target_page_ids:
        page = Page.objects.get(pk=page_id)
        page_mei_path = page.get_mei_path()
        mei_paths.append(str(page_mei_path))

    # the list of paths going into the combiner should be an ordered
    # sequence corresponding to the sequence of uploaded pages
    mc = MeiCombiner(mei_paths)
    mc.combine()
    combined_mei = mc.get_mei()

    return {
        'mei': combined_mei
    }

class CombineMei(JobBase):
    name = 'Combine all MEI files'
    slug = 'combine-mei'
    input_type = JobType.CORRECTED_MEI
    output_type = JobType.END
    description = 'Make a single MEI file out of all images'
    show_during_wf_create = True
    is_automatic = True
    outputs_image = False
    all_pages = True
    task = combine_mei
