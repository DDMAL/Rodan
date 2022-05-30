import os
from binascii import a2b_base64
from rodan.settings import MEDIA_URL, MEDIA_ROOT
from rodan.jobs.base import RodanTask
from django.conf import settings
import json
import numpy as np
import cv2 as cv


def media_file_path_to_public_url(media_file_path):
    chars_to_remove = len(MEDIA_ROOT)
    return os.path.join(MEDIA_URL, media_file_path[chars_to_remove:])


def get_iiif_query(resource_path):
    resource_path = resource_path.split('/')
    resource_path.remove('')
    resource_path.remove('rodan')
    resource_path.remove('data')
    del resource_path[-1]  # last element is the original uncoverted file
    resource_path.append('diva')
    resource_path.append('image.jp2')
    resource_path = '%2F'.join(resource_path)

    server_url = settings.IIPSRV_URL
    query = server_url + '?IIIF=' + resource_path

    return query


def get_image_dimensions(resource_path):
    """
    returns the image dimensions in the following format [height, width]
    """
    resource_path = resource_path.split('/')
    del resource_path[-1]   # last element is the original uncoverted file
    resource_path.append('diva')
    resource_path.append('measurement.json')
    resource_path = '/'.join(resource_path)

    data = json.load(open(resource_path))
    return [data['dims']['max_h'][-1], data['dims']['max_w'][-1]]


def get_images(resource_path):
    query_url = get_iiif_query(resource_path)
    height, width = get_image_dimensions(resource_path)
    return [
            {
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "resource": {
                    "@id": query_url,
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "height":height,
                    "width":width,
                    "service": {
                        "@context": "http://iiif.io/api/image/2/context.json", "@id": query_url, "profile": "http://iiif.io/api/image/2/level2.json"
                        }
                    },
                "on": "https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/canvas/folio-001r.json"
                }
            ]


def create_canvases(resource_path):
    height, width = get_image_dimensions(resource_path)
    data = {}
    data['@id'] = 'https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/canvas/folio-001r.json'
    data['@type'] = 'sc:Canvas'
    data['label'] = 'Folio 001r'
    data['height'] = height
    data['width'] = width
    data['images'] = get_images(resource_path)
    return [data]


def create_sequences(resource_path):
    data = {}
    data['@type'] = 'sc:Sequence'
    data['canvases'] = create_canvases(resource_path)
    return [data]


def create_metadata(resource_path):
    return [
            {"label": "Date", "value": "1554-5"},
            {"label": "Siglum", "value": "CDN-Hsmu M2149.L4"},
            {"label": "Provenance", "value": "Salzinnes"}
            ]


def create_json(resource_path):
    data = {}
    data['@context'] = 'http://iiif.io/api/presentation/2/context.json'
    data['@id'] = 'https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/manifest.json'
    data['@type'] = 'sc:Manifest'
    data['label'] = 'Salzinnes, CDN-Hsmu M2149.L4'
    data['metadata'] = create_metadata(resource_path)
    data['description'] = 'Image'
    data['sequences'] = create_sequences(resource_path)
    return json.dumps(data)


class PixelInteractive(RodanTask):
    name = 'Pixel_js'
    author = 'Zeyad Saleh, Ke Zhang & Andrew Hankinson'
    description = 'Pixel-level ground truth creation and correction'
    settings = {
            'title': 'Options',
            'type': 'object',
            'properties': {
                'Output Mask': {
                    'type': 'boolean',
                    'default': False
                }
            },
            'job_queue': 'Python2',
    }
    enabled = True
    category = 'Diva - Pixel.js'
    interactive = True
    input_port_types = [
            {
                'name': 'Image',
                'resource_types': lambda mime: mime.startswith('image/'),
                'minimum': 1,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 1 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 2 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 3 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 4 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 5 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'PNG - Layer 6 Input',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                    'name': 'PNG - Layer 7 Input',
                    'resource_types': ['image/rgba+png'],
                    'minimum': 0,
                    'maximum': 1,
                    'is_list': False
                    },
            ]
    output_port_types = [
            # {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
            {
                'name': 'rgba PNG - Layer 0 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 1,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 1 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 2 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 3 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 4 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 5 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                'name': 'rgba PNG - Layer 6 Output',
                'resource_types': ['image/rgba+png'],
                'minimum': 0,
                'maximum': 1,
                'is_list': False
                },
            {
                    'name': 'rgba PNG - Layer 7 Output',
                    'resource_types': ['image/rgba+png'],
                    'minimum': 0,
                    'maximum': 1,
                    'is_list': False
                    },
            {
                    'name': 'rgba PNG - Layer 8 Output',
                    'resource_types': ['image/rgba+png'],
                    'minimum': 0,
                    'maximum': 1,
                    'is_list': False
                    },
            ]

    def get_my_interface(self, inputs, settings):
        # Get input.
        layer_urls = []

        query_url = get_iiif_query(inputs['Image'][0]['resource_path'])

        for i in range(1, 8):
            if 'PNG - Layer {} Input'.format(i) in inputs:
                layer_path = inputs['PNG - Layer {} Input'.format(i)][0]['resource_path']
                layer_urls.append(media_file_path_to_public_url(layer_path))

        # Create data to pass.
        data = {
                'json': create_json(inputs['Image'][0]['resource_path']),
                'layer_urls': layer_urls,
                }
        return ('index.html', data)

    def run_my_task(self, inputs, settings, outputs):
        if '@done' not in settings:
            return self.WAITING_FOR_INPUT()

        list = settings['@user_input']    # List passed having the image data (base 64) from all layer

        # Get source image
        background = cv.imread(inputs['Image'][0]['resource_path'], cv.IMREAD_COLOR)

        for i in range(0, len(list)):
            port = "rgba PNG - Layer %d Output" % (i)
            if port in outputs:
                outfile_path = outputs[port][0]['resource_path']
                data = list[i].split(',')[1]    # Remove header from the base 64 string
                missing_padding = len(data) % 4

                if missing_padding != 0:
                    data += '=' * (4 - missing_padding % 4)

                binary_data = a2b_base64(data)   # Parse base 64 image data

                array = np.fromstring(binary_data, np.uint8)

                if settings['Output Mask']:
                    tmp = cv.imdecode(array, cv.IMREAD_UNCHANGED)
                    cv.imwrite(outfile_path + ".png", tmp)
                else:
                    # Create mask for alpha channel
                    layer_image = cv.imdecode(array, cv.IMREAD_GRAYSCALE)
                    _, alpha = cv.threshold(layer_image, 1, 255, cv.THRESH_BINARY)

                    # Set background to black (reduce size) and then make transparent
                    result = cv.bitwise_and(background, background, mask=alpha)
                    b, g, r = cv.split(result)
                    result = cv.merge([b, g, r, alpha], 4)
                    cv.imwrite(outfile_path + ".png", result)  # cv2 needs extension

                os.rename(outfile_path + ".png", outfile_path)
        
        # Cleanup image data from job description when finished.
        if '@done' in settings:
          del settings['@user_input']
        return True

    def validate_my_user_input(self, inputs, settings, user_input):
        return { '@done': True, '@user_input': user_input['user_input'] }

    def my_error_information(self, exc, traceback):
        pass
