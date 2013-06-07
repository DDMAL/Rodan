from django.shortcuts import render
from django.views.generic.base import View
from rest_framework import status

from rodan.models import RunJob
from rodan.models import Result


class RodanInteractiveBaseView(View):
    view_url = ""
    template_name = ""
    data = {}

    def get(self, request, *args, **kwargs):
        if 'runjob' not in request.GET:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        rj_uuid = request.GET['runjob']
        run_job = RunJob.objects.get(uuid=rj_uuid)

        sequence = run_job.workflow_job.sequence
        page = run_job.page

        # if this is the first job in the sequence, the file path is just the original image
        if sequence == 1:
            image_source = run_job.page
        else:
            previous_run_job = RunJob.objects.get(workflow_job__sequence=(sequence - 1),
                                                  workflow_run__uuid=run_job.workflow_run.uuid,
                                                  page = page.uuid)
            image_source = Result.objects.get(run_job__uuid=previous_run_job.uuid)

        data = {'form_url': self.view_url,
                'run_job_uuid': rj_uuid,
                'image_source': image_source}

        for setting in run_job.job_settings:
            data[setting['name']] = setting['default']
        
        return render(request, "{0}/{1}".format('jobs', self.template_name), data)

    def post(self, request, *args, **kwargs):
        if 'run_job_uuid' not in request.POST:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        rj_uuid = request.POST['run_job_uuid']
        run_job = RunJob.objects.get(uuid=rj_uuid)

        for job_setting in run_job.job_settings:
            if job_setting['name'] in request.POST:
                job_setting['default'] = request.POST[job_setting['name']]

        run_job.needs_input = False
        run_job.save()

        return render(request, 'jobs/job_input_done.html')


class CropView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/crop/"
        self.template_name = "crop.html"
        return super(CropView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(CropView, self).post(request, *args, **kwargs)


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


class RotateView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/rotate/"
        self.template_name = "rotate.html"
        return super(RotateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(RotateView, self).post(request, *args, **kwargs)


class SegmentView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/segment/"
        self.template_name = "segmentation.html"
        return super(SegmentView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(SegmentView, self).post(request, *args, **kwargs)


class LuminanceView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/luminance/"
        self.template_name = "luminance.html"
        return super(LuminanceView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(LuminanceView, self).post(request, *args, **kwargs)


class BarlineCorrectionView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/barlinecorrection/"
        self.template_name = "barline-correction.html"
        return super(BarlineCorrectionView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(BarlineCorrectionView, self).post(request, *args, **kwargs)
