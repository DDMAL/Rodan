import utils
from rodan.models.jobs import JobType, JobBase
from rodan.models import Page
from pymei import XmlImport


@utils.rodan_multi_task(inputs='mei')
def combine_mei(mei_path, **kwargs):
    target_page_ids = kwargs['target_page_ids']

    mei_docs = []

    # get the mei of the current page
    mei_docs.append(XmlImport.documentFromFile(str(mei_path)))

    # get the meis of all other pages
    for page_id in target_page_ids:
        page = Page.objects.get(pk=page_id)
        page_mei_path = page.get_mei_path()
        mei_docs.append(XmlImport.documentFromFile(str(page_mei_path)))

    #use mei_docs to merge into one... the first elem of the list is the page thats sending the job
    # and the rest of the list are all other pages waiting to get merged
    all_mei = mei_docs[0]

    return {
        'mei': all_mei,
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
    all_pages = True
    task = combine_mei
