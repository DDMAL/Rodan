from rodan.jobs.base import RodanTask
import json
from celery.utils.log import get_task_logger

# scikit-image, calamari-ocr may not be installed in the Rodan container. Rodan still needs
# to run this file to register the job in the database, so this is a hack to avoid having to
# add "dummy" packages to the rodan containe
try:
    from . import align_to_ocr as align
except (SystemError, ImportError):
    pass


class text_alignment(RodanTask):
    name = 'Text Alignment'
    author = 'Timothy de Reuse'
    description = ('Given a text layer image and a transcript of some text on that page, finds the '
                   'positions of each syllable of text in the transcript on the image. See: '
                   'de Reuse and Fujinaga, "Robust Transcript Alignment on Medieval Chant Manuscripts,"'
                   'in Proceedings of the 2nd International Workshop on Reading Music Systems, 2019')
    enabled = True
    category = 'text'
    interactive = False
    logger = get_task_logger(__name__)

    settings = {
        'title': 'Text Alignment Settings',
        'type': 'object',
        'job_queue': 'GPU',
        'properties': {
            'OCR Model': {
                'type': 'string',
                'enum': ['salzinnes-gothic-2019', 'ms073-2021'],
                'default': 'salzinnes-gothic-2019',
                'description': ('The OCR model used to obtain a \'messy\' transcript, which will '
                                'then be aligned to the given transcript.')
            }
        }
    }

    input_port_types = [{
        'name': 'Text Layer',
        'resource_types': ['image/rgb+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }, {
        'name': 'Transcript',
        'resource_types': ['text/plain'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }
    ]

    output_port_types = [{
        'name': 'Text Alignment JSON',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):
        from skimage import io

        self.logger.info(settings)

        transcript = align.read_file(inputs['Transcript'][0]['resource_path'])
        raw_image = io.imread(inputs['Text Layer'][0]['resource_path'])
        ocr_model_enum = text_alignment.settings['properties']['OCR Model']['enum']
        model_name = ocr_model_enum[settings['OCR Model']]

        self.logger.info('processing image...')
        result = align.process(raw_image, transcript, model_name)

        syl_boxes, _, lines_peak_locs, _ = result

        self.logger.info('writing output to json...')
        outfile_path = outputs['Text Alignment JSON'][0]['resource_path']
        with open(outfile_path, 'w') as file:
            json.dump(align.to_JSON_dict(syl_boxes, lines_peak_locs), file)

        return True
