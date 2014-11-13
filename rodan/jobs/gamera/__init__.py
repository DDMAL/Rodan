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

####### Toolkits
try:
    from gamera.toolkits.background_estimation.plugins import background_estimation
    create_jobs_from_module(background_estimation)
except ImportError as e:
    logger.warning("No Background Estimation Toolkit Installed. Skipping.")

try:
    from gamera.toolkits.border_removal.plugins import border_removal
    create_jobs_from_module(border_removal)
except ImportError as e:
    logger.warning("No Border Removal Toolkit Installed. Skipping.")

try:
    from gamera.toolkits.lyric_extraction.plugins import border_lyric
    from gamera.toolkits.lyric_extraction.plugins import lyricline
    from gamera.toolkits.lyric_extraction.plugins import lyric_extractor
    create_jobs_from_module(border_lyric)
    create_jobs_from_module(lyricline)
    create_jobs_from_module(lyric_extractor)
except ImportError as e:
    logger.warning("No Lyric Extraction Toolkit Installed. Skipping.")

try:
    from gamera.toolkits.musicstaves.plugins import musicstaves_plugins
    create_jobs_from_module(musicstaves_plugins)
except ImportError as e:
    logger.warning("No Music Staves Toolkit Installed. Skipping.")

try:
    from gamera.toolkits.rodan_plugins.plugins.rdn_rotate import rdn_rotate
    from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
    from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
    create_jobs_from_module(rdn_rotate, interactive=True)
    create_jobs_from_module(rdn_despeckle, interactive=True)
    create_jobs_from_module(rdn_despeckle, interactive=False)
    create_jobs_from_module(rdn_crop, interactive=True)
except ImportError as e:
    logger.warning("The Rodan Plugins have not been installed. Skipping.")

try:
    from gamera.toolkits.staffline_removal.plugins import staff_removal
    create_jobs_from_module(staff_removal)
except ImportError as e:
    logger.warning("No Staff Removal Toolkit Installed. Skipping.")



"""
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
