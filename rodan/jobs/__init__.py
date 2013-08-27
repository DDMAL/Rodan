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

print "Loading Rodan Jobs"

try:
    from rodan.jobs.gamera import binarization
    binarization.load_module()
except ImportError as e:
    print "Trouble loading the Gamera binarization plugins. Is Gamera installed?"

try:
    from rodan.jobs.gamera import threshold
    threshold.load_module()
except ImportError as e:
    print "Trouble loading the Gamera threshold plugins. Is Gamera installed?"

try:
    from rodan.jobs.gamera import image_conversion
    image_conversion.load_module()
except ImportError as e:
    print "Trouble loading the Gamera image_conversion plugins. Is Gamera installed?"

try:
    from rodan.jobs.gamera import transformation
    transformation.load_module()
except ImportError as e:
    print "Trouble loading the Gamera transformation plugins. Is Gamera installed?"

try:
    from rodan.jobs.gamera.toolkits import rodan_plugins
    rodan_plugins.load_module()
except ImportError as e:
    print "The Rodan Plugins have not been installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import border_removal
    border_removal.load_module()
except ImportError as e:
    print "No Border Removal Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import staff_removal
    staff_removal.load_module()
except ImportError as e:
    print "No Staff Removal Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import background_estimation
    background_estimation.load_module()
except ImportError as e:
    print "No Background Estimation Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import lyric_extraction
    lyric_extraction.load_module()
except ImportError as e:
    print "No Lyric Extraction Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import musicstaves
    musicstaves.load_module()
except ImportError as e:
    print "No Music Staves Toolkit Installed. Skipping."

##########

try:
    from rodan.jobs.diva import to_jpeg2000
    to_jpeg2000.load_module()
except ImportError as e:
    print "No Diva JPEG2000 converter Installed. Skipping. ", e

try:
    from rodan.jobs.gamera.custom.poly_mask import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Poly Mask job not installed. Skipping", e

try:
    from rodan.jobs.gamera.custom.border_removal import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Border Removal job not installed. Skipping", e

try:
    from rodan.jobs.gamera.custom.segmentation import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Segmentation job not installed. Skipping", e

try:
    from rodan.jobs.gamera.custom.neume_classification import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Classification job not installed. Skipping", e

try:
    from rodan.jobs.gamera.custom.staff_removal import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom RT Staff Removal job not installed. Skipping", e

try:
    from rodan.jobs.gamera.custom.pitch_finding import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Pitch Finding job not installed. Skipping", e

try:
    from rodan.jobs.neon import module_loader
    module_loader.load_module()
except ImportError as e:
    print "Custom Pitch Correction job not installed. Skipping", e


## Periodic Tasks
try:
    from rodan.jobs.periodic_tasks.classifier_ga_optimization import OptimizeAllClassifiersTask
except ImportError as e:
    print "Classifier optimization periodic task not installed. Skipping", e

#Development
try:
    from rodan.jobs.util.devdummyjobs import load_wfjobuuid
    load_wfjobuuid()
except ImportError as e:
    print "DEV: The dummy job could not be loaded properly. Skipping"
    print e
