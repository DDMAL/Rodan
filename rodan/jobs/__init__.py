"""
    The main jobs loading mechanism.

    This directory should be structured in terms of which system they are "wrapping". For example,
    there is a "gamera" directory which contains the code for wrapping Gamera functions. Should we
    wish to integrate another OMR system, a new directory should be created to hold the code for that system.

    You can then import the sub-modules for each system in this file. Please make sure to wrap them
    in an import try/catch, since failure to import a module if it is not installed will prevent Rodan
    from starting. The try/catch will allow a graceful degradation with a message that a particular set of modules
    could not be loaded.

    Each job that is wrapped must define a "load_module()" method. Depending on the complexity of the system
    being wrapped, this may be a very simple or a very complex method, but its main function is to ensure
    that the jobs being imported are placed in the database and registered with Celery.

    For the Gamera modules, you can find the module loading code in the `module_loader.py` file. More documentation
    is available there.

    For each job, you must also define how celery will execute it. For the Gamera modules, this code is
    located in the `celery_task.py` file, which implements the `run()` method of a Celery task.

    Any new Tasks that are defined must also implement the `on_success()` method and use it to create
    thumbnail for any results. (See gamera/celery_task.py: GameraTask.on_success()). This should use the methods
    in the `helpers` directory, since this will automatically offload all thumbnailing to Celery as well.
"""
import logging
logger = logging.getLogger('rodan')

logger.warning("Loading Rodan Jobs")

try:
    from rodan.jobs.gamera import binarization
    binarization.load_module()
except ImportError as e:
    logger.warning("Trouble loading the Gamera binarization plugins. Is Gamera installed?")

# try:
#     from rodan.jobs.gamera import threshold
#     threshold.load_module()
# except ImportError as e:
#     logger.warning("Trouble loading the Gamera threshold plugins. Is Gamera installed?")

# try:
#     from rodan.jobs.gamera import image_conversion
#     image_conversion.load_module()
# except ImportError as e:
#     logger.warning("Trouble loading the Gamera image_conversion plugins. Is Gamera installed?")

# try:
#     from rodan.jobs.gamera import transformation
#     transformation.load_module()
# except ImportError as e:
#     logger.warning("Trouble loading the Gamera transformation plugins. Is Gamera installed?")

# try:
#     from rodan.jobs.gamera.toolkits import rodan_plugins
#     rodan_plugins.load_module()
# except ImportError as e:
#     logger.warning("The Rodan Plugins have not been installed. Skipping.")

# try:
#     from rodan.jobs.gamera.toolkits import border_removal
#     border_removal.load_module()
# except ImportError as e:
#     logger.warning("No Border Removal Toolkit Installed. Skipping.")

# try:
#     from rodan.jobs.gamera.toolkits import staff_removal
#     staff_removal.load_module()
# except ImportError as e:
#     logger.warning("No Staff Removal Toolkit Installed. Skipping.")

# try:
#     from rodan.jobs.gamera.toolkits import background_estimation
#     background_estimation.load_module()
# except ImportError as e:
#     logger.warning("No Background Estimation Toolkit Installed. Skipping.")

# try:
#     from rodan.jobs.gamera.toolkits import lyric_extraction
#     lyric_extraction.load_module()
# except ImportError as e:
#     logger.warning("No Lyric Extraction Toolkit Installed. Skipping.")

# try:
#     from rodan.jobs.gamera.toolkits import musicstaves
#     musicstaves.load_module()
# except ImportError as e:
#     logger.warning("No Music Staves Toolkit Installed. Skipping.")

# ##########

# try:
#     from rodan.jobs.diva import to_jpeg2000
#     to_jpeg2000.load_module()
# except ImportError as e:
#     logger.warning("No Diva JPEG2000 converter Installed. Skipping. {0}".format(e))

# try:
#     from rodan.jobs.gamera.custom.poly_mask import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom Poly Mask job not installed. Skipping".format(e))

# try:
#     from rodan.jobs.gamera.custom.border_removal import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom Border Removal job not installed. Skipping. {0}".format(e))

# try:
#     from rodan.jobs.gamera.custom.segmentation import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom Segmentation job not installed. Skipping. {0}".format(e))

# try:
#     from rodan.jobs.gamera.custom.staff_removal import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom RT Staff Removal job not installed. Skipping. {0}".format(e))

# # try:
# #     from rodan.jobs.gamera.custom.pitch_finding import module_loader
# #     module_loader.load_module()
# # except ImportError as e:
# #     logger.warning("Custom Pitch Finding job not installed. Skipping. {0}".format(e))

# try:
#     from rodan.jobs.neon import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom Pitch Correction job not installed. Skipping. {0}".format(e))

# try:
#     from rodan.jobs.gamera.custom.pixel_segment import module_loader
#     module_loader.load_module()
# except ImportError as e:
#     logger.warning("Custom Pixel Segment job not installed. Skipping. {0}".format(e))


#Development
try:
    from rodan.jobs.devel.dummy_job import load_dummy_job
    load_dummy_job()
except ImportError as e:
    logger.warning("DEV: The dummy job could not be loaded properly. Skipping")

try:
    from rodan.jobs.devel.extract_lyrics import load_dummy_job
    load_dummy_job()
except ImportError as e:
    logger.warning("DEV: The third dummy job could not be loaded. Skipping")

try:
    from rodan.jobs.devel.lyric_line_detection import load_dummy_job
    load_dummy_job()
except ImportError as e:
    logger.warning("DEV: The fourth dummy job could not be loaded. Skipping")

