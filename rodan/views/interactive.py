from django.shortcuts import render
from django.views.generic.base import View

from rodan.models import RunJob
from rodan.models import Result


class RodanInteractiveBaseView(View):
    view_url = ""
    template_name = ""

    def get(self, request, *args, **kwargs):
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
                "form_url": self.view_url,
                "run_job_uuid": rj_uuid
            }
            return render(request, "{0}/{1}".format('jobs', self.template_name), data)
        else:
            return render(request, 'jobs/bad_request.html')

    def post(self, request, *args, **kwargs):
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


class CropView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/crop/"
        self.template_name = "crop.html"
        return super(CropView, self).get(request, *args, **kwargs)

    #Override post because 'imw' should be optional for the client. 
    def post(self, request, *args, **kwargs):
        if 'run_job_uuid' in request.POST:
            rj_uuid = request.POST['run_job_uuid']
            run_job = RunJob.objects.get(uuid=rj_uuid)

            run_job_settings = ('ulx', 'uly', 'lrx', 'lry')

            # check if all required job_settings have been provided in the POST
            if all(job_setting in request.POST for job_setting in run_job_settings):
                # change all the job_settings values of the run_job to the new values
                # (note that the coordinate values need to be scaled since they were taken from a thumbnailed version
                # displayed on the js interface - inside request.POST, the 'imw' parameter hold the value of the width)
                for job_setting in run_job.job_settings:
                    job_setting['default'] = request.POST[job_setting['name']]

                #This is separate because imw is optional.
                #I wonder if there is a more Pythonic way to do this. 
                if 'imw' in request.POST:
                    for setting in run_job.job_settings:
                        if 'imw' == setting['name']:
                            break
                    setting['default'] = request.POST['imw']

                # uncheck needs-input
                run_job.needs_input = False

                # save all the changes
                run_job.save()

                return render(request, 'jobs/job_input_done.html')
            else:
                return render(request, 'jobs/bad_request.html')

class BinariseView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/binarise/"
        self.template_name = "simple-binarise.html"
        return super(BinariseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BinariseView, self).post(request, *args, **kwargs)

class DespeckleView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/despeckle/"
        self.template_name = "despeckle.html"
        return super(DespeckleView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DespeckleView, self).post(request, *args, **kwargs)


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
