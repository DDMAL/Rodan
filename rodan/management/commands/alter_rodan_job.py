import sys

from django.core.management.base import BaseCommand

from rodan.models import Job
from .alter_resource_type import print_table

if sys.version_info.major == 2:
    input = raw_input  # noqa


class Command(BaseCommand):
    """
    """
    help = "List current rodan jobs"

    def add_arguments(self, parser):
        parser.add_argument("-l", "--list", action="store_true", help="Lists all Rodan Jobs")
        parser.add_argument("-d", "--delete-all", action="store_true", help="Remove all jobs")
        parser.add_argument("-u", "--upload-all", action="store_true", help="Upload all jobs")

    def handle(self, *arg, **options):

        if options["list"]:
            print("Here are the currently installed jobs.")

            job_table = [["job name", "job uuid"]]
            [
                job_table.append(
                    [job.name, str(job.uuid)]
                ) for job in Job.objects.all().order_by("name")]
            print_table(job_table)

        elif options["delete_all"]:
            input("Are you sure you want to delete all jobs in the database?")
            input("Are you really sure?")

            for job in Job.objects.all().order_by("name"):
                print("Deleting: {0}".format(job.name))
                job.delete()

            print("...updated.")

        elif options["upload_all"]:
            print("Loading all jobs")
            from rodan.jobs import load  # noqa
