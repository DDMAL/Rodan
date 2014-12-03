import os
import shutil
from rodan.constants import task_status
from rodan.models.resultspackage import ResultsPackage, ResultsPackageStatus
from pybagit.bagit import BagIt
from rodan.helpers.exceptions import BagNotValidError
from rodan.helpers.dbmanagement import exists_in_db
from rodan.helpers.exceptions import PackageCancelledError, ObjectDeletedError
from celery import Task


def _add_result_to_bag(page_dir, runjob, bag):
    # TO-DO: Make error inclusion optional. Make unrun runjob inclustion optional.
    short_job_name = runjob.job_name.split('.')[-1]  # get the last part of job name
    runjob_dir = os.path.join(page_dir, "%s_%s" % (runjob.sequence, short_job_name))

    if runjob.status == task_status.FINISHED:
        os.makedirs(runjob_dir)
        result_extenstion = os.path.splitext(runjob.result.get().result.path)[1]
        result_filename = "result" + result_extenstion  # use filename with proper extenstion
        with open(runjob.result.get().result.path, 'rb') as f:
            with open(os.path.join(runjob_dir, result_filename), 'wb') as newf:
                newf.write(f.read())

    elif runjob.status == task_status.FAILED:
        os.makedirs(runjob_dir)
        with open(os.path.join(runjob_dir, 'error.txt'), 'w') as f:
            f.write("Error Summary: ")
            f.write(runjob.error_summary)
            f.write("\n\nError Details:\n")
            f.write(runjob.error_details)


def _ensure_db_state(resultspackage):
    if not exists_in_db(resultspackage):
        raise ObjectDeletedError("The resultspackage has been deleted. Aborting and scheduling clean up of directory...")

    if resultspackage.status == ResultsPackageStatus.CANCELLED:
        raise PackageCancelledError("The resultspackage has been cancelled. Aborting and scheduling clean up of directory...")


def _update_progress(resultspackage, progress):
    resultspackage.percent_completed = int(progress)
    resultspackage.save()


class PackageResultTask(Task):
    name = 'rodan.helpers.resultspackagemanager.package_results'
    ignore_result = True

    def run(self, package_id, *args, **kwargs):
        resultspackage = ResultsPackage.objects.get(pk=package_id)
        if resultspackage.status == task_status.CANCELLED:
            return

        resultspackage.status = ResultsPackageStatus.PROCESSING
        resultspackage.save()

        runjobs = resultspackage.workflow_run.run_jobs.select_related('page', 'job').all()

        if not resultspackage.pages.exists():
            pages = set()
            for runjob in runjobs:
                pages.add(runjob.page)
        else:
            pages = resultspackage.pages.all()

        jobs = resultspackage.jobs.all()
        self.package_path = resultspackage.package_path

        # The chunks are intervals used to update the percent_completed field.
        if len(pages) > 0:
            page_chunk = 70.00 / len(pages)
        completed = 0.0

        bag = BagIt(resultspackage.bag_path)

        for page in pages:
            page_dir = os.path.join(bag.data_directory, page.name)
            os.makedirs(page_dir)
            page_runjobs = runjobs.filter(page=page)

            if not jobs:
                # If no jobs are provided, we will just make a list of jobs from the available runjobs.
                jobs = []
                if len(page_runjobs) > 0:
                    runjob_chunk = page_chunk / len(page_runjobs)

                for runjob in page_runjobs:
                    _add_result_to_bag(page_dir, runjob, bag)

                    completed += runjob_chunk
                    _ensure_db_state(resultspackage)
                    _update_progress(resultspackage, completed)

                    if runjob.workflow_job.job not in jobs:
                        jobs.append(runjob.workflow_job.job)

            else:
                if len(jobs) > 0:
                    job_chunk = page_chunk / len(jobs)

                for job in jobs:
                    matcthing_runjobs = page_runjobs.filter(workflow_job__job=job)
                    if len(matcthing_runjobs) > 0:
                        runjob_chunk = job_chunk / len(matcthing_runjobs)

                    for runjob in matcthing_runjobs:
                        _add_result_to_bag(page_dir, runjob, bag)

                        completed += runjob_chunk
                        _ensure_db_state(resultspackage)
                        _update_progress(resultspackage, completed)

        bag.update()
        errors = bag.validate()
        if not bag.is_valid:
            _ensure_db_state(resultspackage)
            resultspackage.status = ResultsPackageStatus.FAILED
            resultspackage.save()
            raise BagNotValidError("The bag failed validation.\n" + str(errors))

        bag.package(resultspackage.package_path, method='zip')
        resultspackage.download_url = resultspackage.file_url
        resultspackage.percent_completed = 100
        resultspackage.status = ResultsPackageStatus.COMPLETE

        # If pages and jobs were not provided, we populate these fields now
        # since we have figured them out.
        resultspackage.pages = pages
        resultspackage.jobs = jobs

        _ensure_db_state(resultspackage)
        resultspackage.save()
        shutil.rmtree(resultspackage.bag_path)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        rp = ResultsPackage.objects.filter(pk=args[0])
        if rp.exists():
            rp = rp.get()
            rp.status = ResultsPackageStatus.FAILED
            rp.save()
        if os.path.exists(self.package_path):
            shutil.rmtree(self.package_path)
