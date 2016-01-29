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
from django.conf import settings
from rodan.models.resourcetype import load_predefined_resource_types
load_predefined_resource_types()  # set up ResourceTypes

import logging
logger = logging.getLogger('rodan')
logger.warning("Loading Rodan Jobs")
import rodan.jobs.core
import rodan.jobs.master_task

from rodan.jobs import module_loader, package_versions

from rodan.models import Job, WorkflowJob

job_list = list(Job.objects.all().values_list("name", flat=True))
for package_name in settings.RODAN_JOB_PACKAGES:
    def set_version(module):
        package_versions[package_name] = getattr(module, '__version__', 'n/a')
    module_loader(package_name, set_version)  # RodanTaskType will update `job_list`

UPDATE_JOBS = getattr(settings, "_update_rodan_jobs", False)
if job_list:  # there are database jobs that are not registered. Should delete them.
    if not UPDATE_JOBS:
        raise ValueError("The following jobs are in database but not registered in the code. Perhaps they have been deleted in the code but not in the database. Try to run `manage.py migrate` to confirm deleting them:\n{0}".format('\n'.join(job_list)))
    else:
        for j_name in job_list:
            confirm_delete = raw_input("Job `{0}` is in database but not registered in the code. Perhaps it has been deleted in the code but not yet in the database. Confirm deletion (y/N)? ".format(j_name))
            if confirm_delete.lower() == 'y':
                try:
                    Job.objects.get(name=j_name).delete()
                    print "  ..deleted.\n\n"
                except Exception as e:
                    confirm_delete = raw_input("  ..not deleted because of an exception: {0}. Perhaps there are WorkflowJobs using this Job. Confirm deletion of related WorkflowJobs (y/N)? ".format(str(e)))
                    if confirm_delete.lower() == 'y':
                        try:
                            WorkflowJob.objects.filter(job__name=j_name).delete()
                            Job.objects.get(name=j_name).delete()
                            print "  ..deleted. OK\n\n"
                        except Exception as e:
                            print "  ..not deleted because of an exception: {0}. Please fix it manually.\n\n".format(str(e))
                    else:
                        print "  ..not deleted.\n\n"
            else:
                print "  ..not deleted.\n\n"
