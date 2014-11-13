from rodan.jobs.gamera.module_loader import create_jobs_from_module

import logging
logger = logging.getLogger('rodan')

try:
    from gamera.plugins import binarization
    create_jobs_from_module(binarization)
except ImportError as e:
    logger.warning("Trouble loading the Gamera binarization plugins. Is Gamera installed?")

try:
    from gamera.plugins import threshold
    create_jobs_from_module(threshold)
except ImportError as e:
    logger.warning("Trouble loading the Gamera threshold plugins. Is Gamera installed?")

try:
    from gamera.plugins import image_conversion
    create_jobs_from_module(image_conversion)
except ImportError as e:
    logger.warning("Trouble loading the Gamera image_conversion plugins. Is Gamera installed?")

try:
    from gamera.plugins import transformation
    create_jobs_from_module(transformation)
except ImportError as e:
    logger.warning("Trouble loading the Gamera transformation plugins. Is Gamera installed?")
"""
try:
    from rodan.jobs.gamera.toolkits import rodan_plugins
    rodan_plugins.load_module()
except ImportError as e:
    logger.warning("The Rodan Plugins have not been installed. Skipping.")

try:
    from rodan.jobs.gamera.toolkits import border_removal
    border_removal.load_module()
except ImportError as e:
    logger.warning("No Border Removal Toolkit Installed. Skipping.")

try:
    from rodan.jobs.gamera.toolkits import staff_removal
    staff_removal.load_module()
except ImportError as e:
    logger.warning("No Staff Removal Toolkit Installed. Skipping.")

try:
    from rodan.jobs.gamera.toolkits import background_estimation
    background_estimation.load_module()
except ImportError as e:
    logger.warning("No Background Estimation Toolkit Installed. Skipping.")

try:
    from rodan.jobs.gamera.toolkits import lyric_extraction
    lyric_extraction.load_module()
except ImportError as e:
    logger.warning("No Lyric Extraction Toolkit Installed. Skipping.")

try:
    from rodan.jobs.gamera.toolkits import musicstaves
    musicstaves.load_module()
except ImportError as e:
    logger.warning("No Music Staves Toolkit Installed. Skipping.")




try:
    from rodan.jobs.gamera.custom.poly_mask import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom Poly Mask job not installed. Skipping".format(e))

try:
    from rodan.jobs.gamera.custom.border_removal import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom Border Removal job not installed. Skipping. {0}".format(e))

try:
    from rodan.jobs.gamera.custom.segmentation import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom Segmentation job not installed. Skipping. {0}".format(e))

try:
    from rodan.jobs.gamera.custom.staff_removal import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom RT Staff Removal job not installed. Skipping. {0}".format(e))


try:
    from rodan.jobs.gamera.custom.pixel_segment import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom Pixel Segment job not installed. Skipping. {0}".format(e))
"""
