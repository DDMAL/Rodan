from rodan.jobs.base import RodanTask
from pytz import UTC
from uuid import uuid4
import datetime
import json


class Neon(RodanTask):
    name = 'Neon'
    author = 'Juliette Regimbal & Zoe McLennan'
    description = 'Neume Editor Online'
    settings = {'job_queue': 'Python2'}
    enabled = True
    category = 'Pitch Correction'
    interactive = True

    input_port_types = [
        {
            'name': 'MEI',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/mei+xml']
        },
        {
            'name': 'Image',
            'minimum': 1,
            'maximum': 1,
            'resource_types': lambda mime: mime.endswith('png')
        },
    ]
    output_port_types = [
        {
            'name': 'Corrected',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/mei+xml']
        },
    ]

    def get_my_interface(self, inputs, settings):
        t = 'editor.html'

        if '@manifestText' not in settings:
            settings['@manifestText'] = self.generate_manifest_text(inputs)
        c = {'manifestText': settings['@manifestText']}

        return (t, c)

    def run_my_task(self, inputs, settings, outputs):
        if '@done' not in settings:
            return self.WAITING_FOR_INPUT()
        outfile_path = outputs['Corrected'][0]['resource_path']
        outfile = open(outfile_path, 'w')
        correctedMEI = settings['@user_input']
        outfile.write(correctedMEI)
        outfile.close()
        return True

    def validate_my_user_input(self, inputs, settings, user_input):
        return {'@done': True, '@user_input': user_input['user_input']}

    def my_error_information(self, exc, traceback):
        pass

    def generate_manifest_text(self, inputs):

        manifest = {
            '@context': 'https://ddmal.music.mcgill.ca/Neon/contexts/1/manifest.jsonld',
            'mei_annotations': []
        }
        manifest['title'] = 'Rodan-generated Manifest'
        manifest['@id'] = 'urn:uuid' + str(uuid4())
        manifest['timestamp'] = datetime.datetime.now(tz=UTC).isoformat()

        if len(inputs['Image']) > 0:
            manifest['image'] = inputs['Image'][0]['resource_url']
            annotation = {
                'id': 'urn:uuid' + str(uuid4()),
                'type': 'Annotation',
                'body': inputs['MEI'][0]['resource_url'],
                'target': inputs['Image'][0]['resource_url']
            }
            manifest['mei_annotations'].append(annotation)

        return json.dumps(manifest)
