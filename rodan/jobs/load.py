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
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from rodan.models import Job, WorkflowJob, ResourceType, Resource, ResourceList
import logging, os, sys
import yaml

if sys.version_info.major == 2:
    input = raw_input

logger = logging.getLogger('rodan')
UPDATE_JOBS = getattr(settings, "_update_rodan_jobs", False)  # set when python manage.py migrate

# Set up ResourceTypes
logger.warning("Loading Rodan ResourceTypes")
resourcetypes = {
    "application/octet-stream": [{
        "description": "Unknown type",  # RFC 2046
        "extension": "",
        "package_name": "built-in"
    }],
    "application/zip": [{
        "description": "Package",
        "extension": "zip",
        "package_name": "built-in"
    }],
    "application/json": [{
        "description": "JSON",
        "extension": "json",
        "package_name": "built-in"
    }],
    "text/plain": [{
        "description": "Plain text",
        "extension": "txt",
        "package_name": "built-in"
    }]
} # core resourcetypes

## load types from registered job packages
base_path = os.path.dirname(settings.PROJECT_PATH)
for package_name in settings.RODAN_JOB_PACKAGES:
    rel_path = os.sep.join(package_name.split('.'))
    resource_type_path = os.path.join(base_path, rel_path, 'resource_types.yaml')
    if os.path.isfile(resource_type_path):
        logger.info("searching " + resource_type_path + " for custom MIME resource types")
        with open(resource_type_path, 'r') as f:
            resource_types = yaml.load(f)
            for rt in resource_types:
                if rt['mimetype'] not in resourcetypes:
                    resourcetypes[rt['mimetype']] = []
                resourcetypes[rt['mimetype']].append({
                    'description': rt.get('description', ''),
                    'extension': rt.get('extension', ''),
                    'package_name': package_name
                })
                logger.info("resource type " + rt['mimetype'] + " found")

## check database for updating registered ones
registered_rts = {}
for rt in ResourceType.objects.all():
    registered_rts[rt.mimetype] = {
        "description": rt.description,
        "extension": rt.extension,
    }
def multiple_choice(field_name):
    print("  Multiple {0}s are found")

for mimetype, definitions in resourcetypes.items():
    if len(definitions) == 0: continue
    if mimetype not in registered_rts: # If not yet exist in DB:
        if not UPDATE_JOBS:
            raise ImproperlyConfigured('The catalogue of local ResourceTypes does not match the ones in database: local ResourceType `{0}` has not been registered. Please run `manage.py migrate` on Rodan server to update the database.')
        else:
            print("Adding {0}...  ".format(mimetype))
            possible_descriptions = {}
            possible_extensions = {}
            for d in definitions:
                if d['description']:
                    if d['description'] not in possible_descriptions:
                        possible_descriptions[d['description']] = []
                    possible_descriptions[d['description']].append(d['package_name'])
                if d['extension']:
                    if d['extension'] not in possible_extensions:
                        possible_extensions[d['extension']] = []
                    possible_extensions[d['extension']].append(d['package_name'])

            if len(possible_descriptions.keys()) == 0:
                description = ''
            elif len(possible_descriptions.keys()) == 1:
                description = possible_descriptions.keys()[0]
            else:
                print("\n  Multiple descriptions found for {0}:".format(mimetype))
                choices = []
                for idx, tup in enumerate(possible_descriptions.items()):
                    desc, packages = tup
                    choices.append(desc)
                    print("    #{0}: {1} (from {2})".format(idx+1, desc, ", ".join(packages)))
                answer = input("  Choose a description (#1, #2, ...) or enter yours: ")
                if answer.startswith('#') and answer[1:].isdigit() and 0 < int(answer[1:]) <= len(choices):
                    description = choices[int(answer[1:])-1]
                    print("Your choice: {0}".format(description))
                else:
                    description = answer

            if len(possible_extensions.keys()) == 0:
                extension = ''
            elif len(possible_extensions.keys()) == 1:
                extension = possible_extensions.keys()[0]
            else:
                print("\n  Multiple extensions found for {0}:".format(mimetype))
                choices = []
                for idx, tup in enumerate(possible_extensions.items()):
                    ext, packages = tup
                    choices.append(ext)
                    print("    #{0}: {1} (from {2})".format(idx+1, ext, ", ".join(packages)))
                answer = input("  Choose an extension (#1, #2, ...) or enter yours: ")
                if answer.startswith('#') and answer[1:].isdigit() and 0 < int(answer[1:]) <= len(choices):
                    extension = choices[int(answer[1:])-1]
                    print("Your choice: {0}".format(extension))
                else:
                    extension = answer

            r = ResourceType.objects.create(mimetype=mimetype,
                                            description=description,
                                            extension=extension)
            print("Added {0} with description='{1}' and extension='{2}'".format(r.mimetype, r.description, r.extension))
    else:  # exist in DB. Don't touch ([TODO]: for now, perhaps we want the server maintainer to change it somehow...)
        del registered_rts[mimetype]

## delete removed ones
if registered_rts:  # if there are still registered ones
    if not UPDATE_JOBS:
        raise ImproperlyConfigured("The following ResourceTypes are in database but not registered in the code. Perhaps they have been deleted in the code but not in the database. Try to run `manage.py migrate` to confirm deleting them:\n{0}".format('\n'.join(registered_rts.keys())))
    else:
        for mimetype, info in registered_rts.items():
            confirm_delete = input("ResourceType `{0}` is in database but not registered in the code. Perhaps it has been deleted in the code but not yet in the database. Confirm deletion (y/N)? ".format(mimetype))
            if confirm_delete.lower() == 'y':
                try:
                    ResourceType.objects.get(mimetype=mimetype).delete()
                    print("  ..deleted.\n\n")
                except Exception as e:
                    confirm_delete = input("  ..not deleted because of an exception: {0}. Perhaps there are Resources or ResourceLists using this ResourceType. Confirm deletion of related Resources (y/N)? ".format(str(e)))
                    if confirm_delete.lower() == 'y':
                        try:
                            Resource.objects.filter(resource_type__mimetype=mimetype).delete()
                            ResourceType.objects.get(mimetype=mimetype).delete()
                            print("  ..deleted. OK\n\n")
                        except Exception as e:
                            print("  ..not deleted because of an exception: {0}. Please fix it manually.\n\n".format(str(e)))
                    else:
                        print("  ..not deleted.\n\n")
            else:
                print("  ..not deleted.\n\n")






# Set up Jobs
logger.warning("Loading Rodan Jobs")
import rodan.jobs.core
import rodan.jobs.master_task

from rodan.jobs import module_loader, package_versions


job_list = list(Job.objects.all().values_list("name", flat=True))
for package_name in settings.RODAN_JOB_PACKAGES:
    def set_version(module):
        package_versions[package_name] = getattr(module, '__version__', 'n/a')
    module_loader(package_name, set_version)  # RodanTaskType will update `job_list`

if job_list:  # there are database jobs that are not registered. Should delete them.
    if not UPDATE_JOBS:
        raise ImproperlyConfigured("The following jobs are in database but not registered in the code. Perhaps they have been deleted in the code but not in the database. Try to run `manage.py migrate` to confirm deleting them:\n{0}".format('\n'.join(job_list)))
    else:
        for j_name in job_list:
            confirm_delete = input("Job `{0}` is in database but not registered in the code. Perhaps it has been deleted in the code but not yet in the database. Confirm deletion (y/N)? ".format(j_name))
            if confirm_delete.lower() == 'y':
                try:
                    Job.objects.get(name=j_name).delete()
                    print("  ..deleted.\n\n")
                except Exception as e:
                    confirm_delete = input("  ..not deleted because of an exception: {0}. Perhaps there are WorkflowJobs using this Job. Confirm deletion of related WorkflowJobs (y/N)? ".format(str(e)))
                    if confirm_delete.lower() == 'y':
                        try:
                            WorkflowJob.objects.filter(job__name=j_name).delete()
                            Job.objects.get(name=j_name).delete()
                            print("  ..deleted. OK\n\n")
                        except Exception as e:
                            print("  ..not deleted because of an exception: {0}. Please fix it manually.\n\n".format(str(e)))
                    else:
                        print("  ..not deleted.\n\n")
            else:
                print("  ..not deleted.\n\n")
