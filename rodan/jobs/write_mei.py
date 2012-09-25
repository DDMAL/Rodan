import utils
from rodan.models.jobs import JobType, JobBase
from rodan.models import Page
from pymei import XmlImport

from mei_resources.meicombine import MeiCombiner

@utils.rodan_multi_task(inputs='mei', others=['page_sequence'])
def combine_mei(mei_path, page_sequence, **kwargs):
    target_page_ids = kwargs['target_page_ids']

    # dictionary of page sequences to mei paths
    pages = {page_sequence: str(mei_path)}

    # get the meis of all other pages
    for page_id in target_page_ids:
        page = Page.objects.get(pk=page_id)
        page_mei_path = page.get_mei_path()
        pages[page.sequence] = str(page_mei_path)

    # ordered_mei is a list of the mei files generated for each page
    # that is in the order of uploaded files
    ordered_mei = [pages[seq] for seq in sorted(pages.iterkeys())]
    mc = MeiCombiner(ordered_mei)
    mc.combine()
    combined_mei = mc.get_mei()

    return {
        'mei': combined_mei,
        'page_ids': target_page_ids
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
