import os
import inspect
from rodan.models.jobs import JobBase

"""
To automatically import all the subclasses of JobBase defined in files in
this directory. Exports the "jobs" variable, which is a dictionary whose keys
are the module names plus the class name (e.g. binarisation.Binarise).
"""

jobs = {}

for filename in os.listdir(os.path.dirname(__file__)):
    if filename == '__init__.py' or filename[-3:] != '.py':
        continue
    module = __import__(filename[:-3], locals(), globals())
    del filename
    for name, job in inspect.getmembers(module):
        try:
            if issubclass(job, JobBase) and not name.endswith('JobBase'):
                jobs[module.__name__ + '.' + name] = job()
        except TypeError:
            pass
