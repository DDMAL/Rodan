"""
This module is for setting CELERY_IMPORTS that indicates Celery where to find tasks.
It is also imported in `rodan.startup` to test whether there are errors in job definitions
by loading Jobs, InputPortTypes and OutputPortTypes into the database.

It imports core Celery tasks of Rodan (such as `master_task`), and imports every vendor's
package. Every vendor is responsible to import its own job definitions in its
`__init__.py`. Vendors should wrap their imports in try/catch statements, since failure to
import a module if it is not installed will prevent Rodan from starting. The try/catch will
allow a graceful degradation with a message that a particular set of modules could not be
loaded.


# How to write Rodan jobs?

See https://github.com/DDMAL/Rodan/wiki/Introduction-to-job-modules


# Why not loading in `__init__.py`?

Because it hinders testing. If we write these imports in `__init__.py`, Rodan will attempt
to load the jobs into production database in the beginning of testing, because there are
some views that import `rodan.jobs`. Thus Rodan won't reinitialize the database as there
are already Job-related objects in the production database, and we cannot test whether
there are errors in job definitions. Therefore, we write imports in a submodule that will
never be executed when importing `rodan.jobs` or other submodules under `rodan.jobs`.
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
