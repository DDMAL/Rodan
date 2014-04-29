import json
import sys
from gamera.core import init_gamera, load_image
from gamera.plugins.pil_io import from_pil
#import Image
#import ImageDraw
from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask


class PixelSegmentTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.lyric_extraction.pixel_segment'

    settings = [{'visibility': False, 'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'image_width', 'type': 'int'},
                {'visibility': False, 'default': None, 'has_default': True, 'name': 'geometries', 'type': 'json'}]

    def preconfigure_settings(self, page_url, settings):
        init_gamera()
        task_image = load_image(page_url)
        miyao_settings = settings.copy()
        del miyao_settings['image_width']
        return {'image_width': task_image.ncols}

    def process_image(self, task_image, settings):
        # Get the returned data.
        try:
            geometries = json.loads(settings['geometries'])
        except ValueError:
            geometries = []

        # Make copy of original
        imageOriginalCopy = task_image.to_pil()

        # For each of the geometries provided, we have to apply the pixel colour to non-white pixels.
        for geometry in geometries:

            # we don't use the alpha component.
            newColour = (geometry['colour'][0], geometry['colour'][1], geometry['colour'][2])

            # Get scaling factor.
            workingWidth = geometry['workingWidth']
            originalWidth = geometry['originalWidth']
            scale = float(originalWidth) / workingWidth

            # For the polygon, create crop box.
            upperLeftX = sys.maxint
            upperLeftY = sys.maxint
            lowerRightX = 0;
            lowerRightY = 0;
            for point in geometry['points']:
                point['x'] = int(point['x'] * scale)
                point['y'] = int(point['y'] * scale)
                upperLeftX = point['x'] if point['x'] < upperLeftX else upperLeftX
                upperLeftY = point['y'] if point['y'] < upperLeftY else upperLeftY
                lowerRightX = point['x'] if point['x'] > lowerRightX else lowerRightX
                lowerRightY = point['y'] if point['y'] > lowerRightY else lowerRightY
            box = (upperLeftX, upperLeftY, lowerRightX, lowerRightY)

            # Crop out the image and get data.
            imageCrop = imageOriginalCopy.crop(box)
            imageCrop.load()
            imagePixelData = list(imageCrop.getdata())

            # Go through pixels.
            for i in range(len(imagePixelData)):
                if imagePixelData[i] != (255, 255, 255):
                    imagePixelData[i] = newColour

            # Apply.
            imageCrop.putdata(imagePixelData)
            imageOriginalCopy.paste(imageCrop, (upperLeftX, upperLeftY, lowerRightX, lowerRightY))

        # Convert back to gamera image and return.
        finalImage = from_pil(imageOriginalCopy)
        return finalImage
