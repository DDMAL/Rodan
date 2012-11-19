import os
import inspect
import pkgutil
from rodan.celery_models.jobbase import JobBase

"""
To automatically import all the subclasses of JobBase defined in files in
this directory. Exports the "jobs" variable, which is a dictionary whose keys
are the module names plus the class name (e.g. binarisation.Binarise).
"""

jobs = {}
prefix = 'rodan.jobs.'
for loader, modname, ispkg in pkgutil.iter_modules(__path__, prefix):
    try:
        module = loader.find_module(modname).load_module(modname)
    except ImportError as e:
        print "Cannot import {0}. Disabling Support {1}".format(modname, e)
        continue

    for name, job in inspect.getmembers(module, inspect.isclass):
        try:
            if issubclass(job, JobBase) and not name.endswith('JobBase'):
                jobs[module.__name__ + '.' + name] = job()
        except TypeError:
            pass
