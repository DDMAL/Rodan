from rodan.models.jobs import JobType, JobBase
from tasks import tasks 

class Classifier(JobBase):
    name = 'Gamera classifier'
    slug = 'classifier'
    input_type = JobType.IMAGE
    output_type = JobType.XML
    description = 'Performs classification on a binarized staff-less image and outputs an xml file'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        tasks.classifier.delay(result_id)
