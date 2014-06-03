import json
import sys
from gamera.core import init_gamera, load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask

class PixelSegmentTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.lyric_extraction.pixel_segment'

    settings = [{'visibility': False, 'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'image_width', 'type': 'int'},
                {'visibility': False, 'default': None, 'has_default': True, 'name': 'geometries', 'type': 'json'}]

    # Preconfiguration setup.
    def preconfigure_settings(self, page_url, settings):

        init_gamera()
        task_image = load_image(page_url)
        miyao_settings = settings.copy()
        del miyao_settings['image_width']
        return {'image_width': task_image.ncols}

    # Given an image and coloured geometries from the associated interactive
    # job, converts non-white pixels in each geometry in the image to the
    # specified colour.
    def process_image(self, task_image, settings):

        # Get the returned data.
        try:
            geometries = json.loads(settings['geometries'])
        except ValueError:
            geometries = []

        # Make copy of original
        imageOriginal = task_image.to_pil()

        # For each of the geometries provided, we have to apply the pixel colour to non-white pixels.
        for geometry in geometries:
            imageOriginal = self._apply_geometry(imageOriginal, geometry)

        # Convert red to white and black to green.
        colour_swap = {(255, 0, 0): (255, 255, 255), (0, 255, 0): (0, 0, 0)}
        box = (0, 0, imageOriginal.size[0], imageOriginal.size[1])
        imageOriginal = self._colour_swap_pixels(imageOriginal, box, colour_swap)

        # Convert back to gamera image and return.
        finalImage = from_pil(imageOriginal)
        return finalImage

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
    def _colour_swap_pixels(self, image, box, colour_swap):
        imageCrop = image.crop(box)
        imageCrop.load()
        imagePixelData = list(imageCrop.getdata())
        for i in range(len(imagePixelData)):
            if (imagePixelData[i] in colour_swap):
                imagePixelData[i] = colour_swap[imagePixelData[i]]
        imageCrop.putdata(imagePixelData)
        image.paste(imageCrop, box)
        return image


