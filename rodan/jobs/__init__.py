"""
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

import rodan.jobs.helpers
import rodan.jobs.master_task
import rodan.helpers.resultspackagemanager

import rodan.jobs.conversion
import rodan.jobs.gamera
import rodan.jobs.diva
import rodan.jobs.neon
