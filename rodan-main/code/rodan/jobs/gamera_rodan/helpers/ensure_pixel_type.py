from rodan.jobs.gamera_rodan.helpers import argconvert
from gamera import enums

def ensure_pixel_type(gamera_image, mimetype):
    target_type = argconvert.convert_mimetype_to_pixel(mimetype)
    if target_type != gamera_image.data.pixel_type:
        if target_type == enums.ONEBIT:
            return gamera_image.to_onebit()
        elif target_type == enums.GREYSCALE:
            return gamera_image.to_greyscale()
        elif target_type == enums.GREY16:
            return gamera_image.to_grey16()
        elif target_type == enums.RGB:
            return gamera_image.to_rgb()
        elif target_type == enums.FLOAT:
            return gamera_image.to_float()
        elif target_type == enums.COMPLEX:
            return gamera_image.to_complex()
        else:
            raise TypeError('Unsupported Gamera type: {0}'.format(target_type))
    else:
        return gamera_image
