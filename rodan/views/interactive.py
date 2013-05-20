from django.shortcuts import render

from rodan.models import RunJob
from rodan.models import Result


def crop(request):
    if request.method == "GET":
        if 'rj_uuid' in request.GET:
            rj_uuid = request.GET['rj_uuid']
            run_job = RunJob.objects.get(uuid=rj_uuid)

            sequence = run_job.workflow_job.sequence

            # if this is the first job in the sequence, the file path is just the original image
            if sequence == 1:
                path_to_image = run_job.page.large_thumb_url
            else:
                previous_run_job = RunJob.objects.get(workflow_job__sequence=(sequence - 1), workflow_run__uuid=run_job.workflow_run.uuid)
                previous_job_result = Result.objects.get(run_job__uuid=previous_run_job.uuid)

                path_to_image = previous_job_result.large_thumb_url

            data = {
                "image": path_to_image,
                "form_url": "/interactive/crop/",  # should probably find a more elegant way of doing this
                "run_job_uuid": rj_uuid
            }
            return render(request, 'jobs/crop.html', data)
        else:
            return render(request, 'jobs/bad_request.html')

    elif request.method == "POST":
        if 'run_job_uuid' in request.POST:
            rj_uuid = request.POST['run_job_uuid']
            run_job = RunJob.objects.get(uuid=rj_uuid)

            run_job_settings = [y['name'] for y in run_job.job_settings]

            # check if all required job_settings have been provided in the POST
            if all(job_setting in request.POST for job_setting in run_job_settings):
                # change all the job_settings values of the run_job to the new values
                # (note that the coordinate values need to be scaled since they were taken from a thumbnailed version
                # displayed on the js interface - inside request.POST, the 'imw' parameter hold the value of the width)
                for job_setting in run_job.job_settings:
                    job_setting['default'] = request.POST[job_setting['name']]

                # uncheck needs-input
                run_job.needs_input = False

                # save all the changes
                run_job.save()

                return render(request, 'jobs/job_input_done.html')
            else:
                return render(request, 'jobs/bad_request.html')


def binarise(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }
    return render(request, 'jobs/simple-binarise.html', data)


def despeckle(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }
    return render(request, 'jobs/despeckle.html', data)


def rotate(request):
    data = {
        "image": "http://placehold.it/1000x1000"  # a placeholder image for now
    }
    return render(request, 'jobs/rotate.html', data)


def segment(request):
    data = {
        "image": "http://placehold.it/1000x1000"  # a placeholder image for now
    }
    return render(request, 'jobs/segmentation.html', data)


def luminance(request):
    data = {
        "medium_thumbnail": "http://placehold.it/400x400",  # a placeholder image for now
    }
    return render(request, 'jobs/luminance.html', data)


def barlinecorrection(request):
    data = {
        "original_image": "http://placehold.it/1000x1000",  # a placeholder image for now
        "small_thumbnail": "http://placehold.it/150x150",
    }

    return render(request, 'jobs/barline-correction.html', data)
