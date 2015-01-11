import json
import sys
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from django.template.loader import get_template


class PixelSegment(RodanTask):
    COLOUR_SWAP_PIXELS_BOX_HEIGHT = 100

    name = 'gamera.lyric_extraction.pixel_segment'
    author = "Ling-Xiao Yang"
    description = "TODO"
    settings = {}
    enabled = True
    category = "Lyric Extraction"
    interactive = True

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if '@geometries' not in settings:
            return self.WAITING_FOR_INPUT()
        else:
            # Given an image and coloured geometries from the associated interactive
            # job, converts non-white pixels in each geometry in the image to the
            # specified colour.
            task_image = load_image(inputs['input'][0]['resource_path'])
            geometries = settings['@geometries']

            # Make copy of original
            imageOriginal = task_image.to_pil()

            # For each of the geometries provided, we have to apply the pixel colour to non-white pixels.
            for geometry in geometries:
                imageOriginal = self._apply_geometry(imageOriginal, geometry)

            # Convert red to white and black to green.
            colour_swap = {(255, 0, 0): (255, 255, 255), (0, 255, 0): (0, 0, 0)}
            imageOriginal = self._colour_swap_pixels(imageOriginal, colour_swap)

            # Convert back to gamera image and return.
            finalImage = from_pil(imageOriginal)
            finalImage.save_PNG(outputs['output'][0]['resource_path'])

    # Returns true iff provided geometry points form a rectangle.
    # It assumes at least 3 points.
    def _is_rectangle(self, geometryPoints):

        if len(geometryPoints) != 4:
            return False

        return ((geometryPoints[0]['y'] == geometryPoints[1]['y'] and
                 geometryPoints[1]['x'] == geometryPoints[2]['x'] and
                 geometryPoints[2]['y'] == geometryPoints[3]['y'] and
                 geometryPoints[3]['x'] == geometryPoints[0]['x']) or
                (geometryPoints[0]['x'] == geometryPoints[1]['x'] and
                 geometryPoints[1]['y'] == geometryPoints[2]['y'] and
                 geometryPoints[2]['x'] == geometryPoints[3]['x'] and
                 geometryPoints[3]['y'] == geometryPoints[0]['y']))

    # Given image and geometry (with colour and working vs original dimensions), apply it to the image.
    def _apply_geometry(self, image, geometry):

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
        geometryTuples = []
        for point in geometry['points']:
            point['x'] = int(point['x'] * scale)
            point['y'] = int(point['y'] * scale)
            upperLeftX = point['x'] if point['x'] < upperLeftX else upperLeftX
            upperLeftY = point['y'] if point['y'] < upperLeftY else upperLeftY
            lowerRightX = point['x'] if point['x'] > lowerRightX else lowerRightX
            lowerRightY = point['y'] if point['y'] > lowerRightY else lowerRightY
            geometryTuples.append((point['x'], point['y']))
        box = (upperLeftX, upperLeftY, lowerRightX, lowerRightY)

        # Change pixels and return.  If the geometry is a rectangle, we use a special
        # method to speed things up that doesn't check for collision.
        if self._is_rectangle(geometry['points']):
            return self._colour_pixels(image, box, newColour, None)
        else:
            return self._colour_pixels(image, box, newColour, geometryTuples)

    # Colours all pixels in the image defined by the box the given colour (except white pixels).
    # If 'collisionGeometry' is provided, it will also check if the given pixel lies within
    # the provided polygon.  (So, if you have a rectangle, don't provided this...it can be null).
    #
    # NOTE: 'collisionGeometry' must be a list of tuples (e.g. [(x, y), (x, y), ...])
    def _colour_pixels(self, image, box, colour, collisionGeometry):

        # Crop out the image and get data.
        imageCrop = image.crop(box)
        imageCrop.load()
        imagePixelData = list(imageCrop.getdata())

        # If collisionGeometry is provided, we need to do collision detection.
        imagePolygonPixelData = None
        if collisionGeometry is not None:
            imageCopy = image.copy()
            draw = ImageDraw.Draw(imageCopy)
            draw.polygon(collisionGeometry, (0, 0, 255), (0, 0, 255))
            del draw
            imageCropPolygon = imageCopy.crop(box)
            imageCropPolygon.load()
            del imageCopy
            imagePolygonPixelData = list(imageCropPolygon.getdata())
            del imageCropPolygon

        # Go through pixels.
        for i in range(len(imagePixelData)):
            if imagePixelData[i] != (255, 255, 255) and \
               (collisionGeometry is None or imagePolygonPixelData[i] == (0, 0, 255)):
                imagePixelData[i] = colour

        # Apply and return.
        imageCrop.putdata(imagePixelData)
        image.paste(imageCrop, box)
        return image

    # Colours all pixels defined in "swap" keys with their "swap" values for the box dimensions.
    # See other '_colour_pixels_' methods...very similar.
    #
    # NOTE: we're not doing the swap on the entire image at once as this can cause memory proglems
    # on large images.  Rather, we do vertical sections of the image one at a time.
    def _colour_swap_pixels(self, image, colour_swap):
        imageHeight = image.size[1]
        count = 0
        done = False
        while not done:
            upperLeftY = count * self.COLOUR_SWAP_PIXELS_BOX_HEIGHT
            lowerRightY = upperLeftY + self.COLOUR_SWAP_PIXELS_BOX_HEIGHT
            if lowerRightY >= imageHeight:
                lowerRightY = imageHeight
                done = True
            box = (0, upperLeftY, image.size[0], lowerRightY)
            imageCrop = image.crop(box)
            imageCrop.load()
            imagePixelData = list(imageCrop.getdata())
            for i in range(len(imagePixelData)):
                if (imagePixelData[i] in colour_swap):
                    imagePixelData[i] = colour_swap[imagePixelData[i]]
            imageCrop.putdata(imagePixelData)
            image.paste(imageCrop, box)
            del imagePixelData
            del imageCrop
            count += 1
        return image

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/pixel_segment.html')
        c = {
            'image_url': inputs['input'][0]['large_thumb_url']
        }
        return (t, c)

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'geometries' not in userdata:
            raise self.ManualPhaseException("Bad data")
        # [TODO] validate userdata
        return {'@geometries': user_input['geometries']}
