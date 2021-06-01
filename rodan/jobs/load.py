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
import os
import sys
import yaml
from rodan.celery import app
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rodan.models import Job, WorkflowJob, ResourceType, Resource, ResourceList  # noqa

import rodan.jobs.core  # noqa
import rodan.jobs.master_task  # noqa
from rodan.jobs import module_loader, package_versions

if sys.version_info.major == 2:
    input = raw_input  # noqa

logger = logging.getLogger("rodan")
UPDATE_JOBS = getattr(
    settings, "_update_rodan_jobs", False
)  # set when python manage.py migrate

# Set up ResourceTypes
logger.warning("Loading Rodan ResourceTypes")
resourcetypes = {
    "application/octet-stream": [
        {
            "description": "Unknown type",  # RFC 2046
            "extension": "",
            "package_name": "built-in",
        }
    ],
    "application/zip": [
        {"description": "Package", "extension": "zip", "package_name": "built-in"}
    ],
    "application/json": [
        {"description": "JSON", "extension": "json", "package_name": "built-in"}
    ],
    "text/plain": [
        {"description": "Plain text", "extension": "txt", "package_name": "built-in"}
    ],
    "image/jp2": [
        {
            "description": "JPEG2000 image",
            "extension": "jp2",
            "package_name": "built-in",
        }
    ],
    "image/png": [
        {"description": "PNG image", "extension": "png", "package_name": "built-in"}
    ],
    "image/rgb+png": [
        {
            # Proper type for all PNGs is image/png
            "description": "RGB PNG image",
            "extension": "png",
            "package_name": "built-in",
        }
    ],
    "image/rgb+jpg": [
        {
            "description": "JPG image file",
            "extension": "jpg",
            "package_name": "built-in",
        }
    ],
    "image/rgba+png": [
        {
            "description": "PNG image file with alpha channel",
            "extension": "png",
            "package_name": "built-in",
        }
    ],
    "keras/model+hdf5": [
        {
            # Should be application/x-hdf5
            "description": "Trained network from Keras framework",
            "extension": "hdf5",
            "package_name": "built-in",
        }
    ],
    "application/gamera+xml": [
        {
            # Should be application/xml or application/x-gamera+xml, etc.
            "description": "Gamera XML file",
            "extension": "xml",
            "package_name": "built-in",
        }
    ],
    "image/onebit+png": [
        {
            "description": "One-bit (black and white) PNG image",
            "extension": "png",
            "package_name": "built-in",
        }
    ],
    "image/greyscale+png": [
        {
            "description": "Greyscale PNG image",
            "extension": "png",
            "package_name": "built-in",
        }
    ],
    "image/grey16+png": [
        {
            "description": "Greyscale 16 PNG image",
            "extension": "png",
            "package_name": "built-in",
        }
    ],
    "application/gamera-polygons+txt": [
        {
            # Should be application/txt or application/x-gamera-polygons+txt
            "description": "Python list of polygons ([[[x,y], [x,y], ...], [[x,y], [x,y], ...], ...])",
            "extension": "txt",
            "package_name": "built-in",
        }
    ],
    "application/mei+xml": [
        {
            # application/x-mei+xml
            "description": "Music Encoding Initiative",
            "extension": "mei",
            "package_name": "built-in",
        }
    ],
    "application/midi": [
        {
            # Should be audio/midi, audio/x-midi
            "description": "Musical Instrumental Digital Interface",
            "extension": "midi",
            "package_name": "built-in",
        }
    ],
    "application/ace+xml": [
        {
            # application/x-ace+xml or application/xml
            "description": "ACE XML",
            "extension": "xml",
            "package_name": "built-in",
        }
    ],
    "application/arff": [
        {"description": "WEKA ARFF", "extension": "arff", "package_name": "built-in"}
    ],
    "application/arff+csv": [
        {"description": "WEKA ARFF CSV", "extension": "csv", "package_name": "built-in"}
    ],
    "application/jsc+txt": [
        {
            # application/x-jsc+txt
            "description": "jSymbolic Configuration Text File",
            "extension": "txt",
            "package_name": "built-in",
        }
    ],
    "text/csv": [
        {
            "description": "Comma Separated Values",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "image/tiff": [
        {"description": "TIFF image", "extension": "tiff", "package_name": "built-in"}
    ],
    "application/ocropus+pyrnn": [
        {
            # application/x-ocropus+pyrnn
            "description": "OCR model trained by OCRopus",
            "extension": "pyrnn",
            "package_name": "built-in",
        }
    ],
    "application/x-musicxml+xml": [
        {
            # application/vnd.recordare.musicxml(+xml)
            "description": "MusicXML",
            "extension": "xml",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_noterest_pandas_series+csv": [
        {
            # Why not just application/x-pandas_series+csv and application/x-pandas_dataframe+csv
            "description": "NoteRest Indexer Result (Pandas Series CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_dissonance_pandas_dataframe+csv": [
        {
            "description": "Dissonance Interval Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_vertical_pandas_series+csv": [
        {
            "description": "Vertical Interval Indexer Result (Pandas Series CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_horizontal_pandas_series+csv": [
        {
            "description": "Horizontal Interval Indexer Result (Pandas Series CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_ngram_pandas_dataframe+csv": [
        {
            "description": "N-gram Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_fermata_pandas_dataframe+csv": [
        {
            "description": "Fermata Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_figuredbass_pandas_dataframe+csv": [
        {
            "description": "Figured Bass Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_measure_pandas_dataframe+csv": [
        {
            "description": "Measure Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_duration_pandas_dataframe+csv": [
        {
            "description": "Duration Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-vis_nbs_pandas_dataframe+csv": [
        {
            "description": "Note Beat Strength Indexer Result (Pandas DataFrame CSV)",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-pandas_dataframe+csv": [
        {
            "description": "Pandas serialized DataFrame csv",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
    "application/x-pandas_series+csv": [
        {
            "description": "Pandas serialized Series csv",
            "extension": "csv",
            "package_name": "built-in",
        }
    ],
}  # core resourcetypes

# load types from registered job packages
base_path = os.path.dirname(settings.PROJECT_PATH)
for package_name in settings.RODAN_JOB_PACKAGES:
    rel_path = os.sep.join(package_name.split("."))
    resource_type_path = os.path.join(base_path, rel_path, "resource_types.yaml")
    if os.path.isfile(resource_type_path):
        logger.info(
            "searching " + resource_type_path + " for custom MIME resource types"
        )
        with open(resource_type_path, "r") as f:
            resource_types = yaml.load(f)
            for rt in resource_types:
                if rt["mimetype"] not in resourcetypes:
                    resourcetypes[rt["mimetype"]] = []
                resourcetypes[rt["mimetype"]].append(
                    {
                        "description": rt.get("description", ""),
                        "extension": rt.get("extension", ""),
                        "package_name": package_name,
                    }
                )
                logger.info("resource type " + rt["mimetype"] + " found")

# check database for updating registered ones
registered_rts = {}
for rt in ResourceType.objects.all():
    registered_rts[rt.mimetype] = {
        "description": rt.description,
        "extension": rt.extension,
    }


def multiple_choice(field_name):
    print("  Multiple {0}s are found")


for mimetype, definitions in resourcetypes.items():
    if len(definitions) == 0:
        continue

    # If not yet exist in DB:
    if mimetype not in registered_rts:
        if not UPDATE_JOBS:
            raise ImproperlyConfigured(
                (
                    "The catalogue of local ResourceTypes does not match the ones in "
                    "database: local ResourceType `{0}` has not been registered. Please"
                    " run `manage.py migrate` on Rodan server to update the database."
                ).format(mimetype)
            )  # noqa
        else:
            print("Adding {0}...  ".format(mimetype))
            possible_descriptions = {}
            possible_extensions = {}
            for d in definitions:
                if d["description"]:
                    if d["description"] not in possible_descriptions:
                        possible_descriptions[d["description"]] = []
                    possible_descriptions[d["description"]].append(d["package_name"])
                if d["extension"]:
                    if d["extension"] not in possible_extensions:
                        possible_extensions[d["extension"]] = []
                    possible_extensions[d["extension"]].append(d["package_name"])

            if len(possible_descriptions.keys()) == 0:
                description = ""
            elif len(possible_descriptions.keys()) == 1:
                description = possible_descriptions.keys()[0]
            else:
                print("\n  Multiple descriptions found for {0}:".format(mimetype))
                choices = []
                for idx, tup in enumerate(possible_descriptions.items()):
                    desc, packages = tup
                    choices.append(desc)
                    print(
                        "    #{0}: {1} (from {2})".format(
                            idx + 1, desc, ", ".join(packages)
                        )
                    )
                answer = input("  Choose a description (#1, #2, ...) or enter yours: ")
                if (
                    answer.startswith("#")
                    and answer[1:].isdigit()
                    and 0 < int(answer[1:]) <= len(choices)
                ):
                    description = choices[int(answer[1:]) - 1]
                    print("Your choice: {0}".format(description))
                else:
                    description = answer

            if len(possible_extensions.keys()) == 0:
                extension = ""
            elif len(possible_extensions.keys()) == 1:
                extension = possible_extensions.keys()[0]
            else:
                print("\n  Multiple extensions found for {0}:".format(mimetype))
                choices = []
                for idx, tup in enumerate(possible_extensions.items()):
                    ext, packages = tup
                    choices.append(ext)
                    print(
                        "    #{0}: {1} (from {2})".format(
                            idx + 1, ext, ", ".join(packages)
                        )
                    )
                answer = input("  Choose an extension (#1, #2, ...) or enter yours: ")
                if (
                    answer.startswith("#")
                    and answer[1:].isdigit()
                    and 0 < int(answer[1:]) <= len(choices)
                ):
                    extension = choices[int(answer[1:]) - 1]
                    print("Your choice: {0}".format(extension))
                else:
                    extension = answer

            r = ResourceType.objects.create(
                mimetype=mimetype, description=description, extension=extension
            )
            print(
                "Added {0} with description='{1}' and extension='{2}'".format(
                    r.mimetype, r.description, r.extension
                )
            )
    else:
        # exist in DB. Don't touch
        # ([TODO]: for now, perhaps we want the server maintainer to change it somehow...)
        del registered_rts[mimetype]

# delete removed ones
if registered_rts:  # if there are still registered ones
    # To keep docker images small, only the main celery queue NEEDS all jobs.
    # if os.environ["CELERY_JOB_QUEUE"] != "celery":
    #     pass
    if not UPDATE_JOBS:
        raise ImproperlyConfigured(
            (
                "The following ResourceTypes are in database but not registered"
                " in the code. Perhaps they have been deleted in the code but "
                "not in the database. Try to run `manage.py migrate` to confirm "
                "deleting them:\n{0}"
            ).format("\n".join(registered_rts.keys()))
        )
    else:
        for mimetype, info in registered_rts.items():
            confirm_delete = input(
                (
                    "ResourceType `{0}` is in database but not registered in the "
                    "code. Perhaps it has been deleted in the code but not yet in"
                    " the database. Confirm deletion (y/N)? "
                ).format(mimetype)
            )
            if confirm_delete.lower() == "y":
                try:
                    ResourceType.objects.get(mimetype=mimetype).delete()
                    print("  ..deleted.\n\n")
                except Exception as e:
                    confirm_delete = input(
                        (
                            "  ..not deleted because of an exception: {0}. Perhaps "
                            "there are Resources or ResourceLists using this "
                            "ResourceType. Confirm deletion of related Resources (y/N)? "
                        ).format(str(e))
                    )
                    if confirm_delete.lower() == "y":
                        try:
                            Resource.objects.filter(
                                resource_type__mimetype=mimetype
                            ).delete()
                            ResourceType.objects.get(mimetype=mimetype).delete()
                            print("  ..deleted. OK\n\n")
                        except Exception as e:
                            print(
                                (
                                    "  ..not deleted because of an exception: {0}. Please"
                                    " fix it manually.\n\n"
                                ).format(str(e))
                            )
                    else:
                        print("  ..not deleted.\n\n")
            else:
                print("  ..not deleted.\n\n")


# Setup Jobs
logger.warning("Loading Rodan Jobs")

job_list = list(Job.objects.all().values_list("name", flat=True))
for package_name in settings.RODAN_JOB_PACKAGES:

    def set_version(module):
        package_versions[package_name] = getattr(module, "__version__", "n/a")

    module_loader(package_name, set_version)  # RodanTaskType will update `job_list`

"""
In Celery 4.0 and above tasks are not auto registered. While Rodan may see the tasks 
normally, it fails to put them into Celery through RodanTask. Thus, it is necessary 
to import the jobs manually below the normal load.py code (so initialization is complete).
We may refactor this later into another file, but right now it works.
"""

from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier
from rodan.jobs.resource_distributor import ResourceDistributor
from rodan.jobs.labeler import Labeler

for job_name in settings.RODAN_PYTHON2_JOBS:

    app.register_task(InteractiveClassifier())

    def set_version(module):
        package_versions[job_name] = getattr(module, "__version__", "n/a")
    module_loader(job_name, set_version)  # RodanTaskType will update `job_list`

for job_name in settings.BASE_JOB_PACKAGES:
    app.register_task(ResourceDistributor())
    app.register_task(Labeler())

    def set_version(module):
        package_versions[job_name] = getattr(module, "__version__", "n/a")
    module_loader(job_name, set_version)  # RodanTaskType will update `job_list`

if job_list:  # there are database jobs that are not registered. Should delete them.
    # To keep docker images small, only the main celery queue NEEDS all jobs.
    if (
        os.environ["CELERY_JOB_QUEUE"] != "celery"
        and os.environ["CELERY_JOB_QUEUE"] != "None"
    ):
        pass
    elif not UPDATE_JOBS:
        raise ImproperlyConfigured(
            (
                "The following jobs are in database but not registered in the code. Perhaps"
                " they have been deleted in the code but not in the database. Try to run "
                "`manage.py migrate` to confirm deleting them:\n{0}"
            ).format("\n".join(job_list))
        )
    else:
        for j_name in job_list:
            confirm_delete = input(
                (
                    "Job `{0}` is in database but not registered in the code. Perhaps it has "
                    "been deleted in the code but not yet in the database. Confirm deletion "
                    "(y/N)? "
                ).format(j_name)
            )
            if confirm_delete.lower() == "y":
                try:
                    Job.objects.get(name=j_name).delete()
                    print("  ..deleted.\n\n")
                except Exception as e:
                    confirm_delete = input(
                        (
                            "  ..not deleted because of an exception: {0}. Perhaps there are "
                            "WorkflowJobs using this Job. Confirm deletion of related "
                            "WorkflowJobs (y/N)? "
                        ).format(str(e))
                    )
                    if confirm_delete.lower() == "y":
                        try:
                            WorkflowJob.objects.filter(job__name=j_name).delete()
                            Job.objects.get(name=j_name).delete()
                            print("  ..deleted. OK\n\n")
                        except Exception as e:
                            print(
                                (
                                    "  ..not deleted because of an exception: {0}. Please fix it"
                                    " manually.\n\n"
                                ).format(str(e))
                            )
                    else:
                        print("  ..not deleted.\n\n")
            else:
                print("  ..not deleted.\n\n")
