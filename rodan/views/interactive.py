import os
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from rest_framework import status

from rodan.models import RunJob
from rodan.models import Result


class RodanInteractiveBaseView(View):
    view_url = ""
    template_name = ""
    data = {}

    def runjob_context(self, runjob, request):
        """
        Provide this method in a subclass to provide extra context
        about the runjob to the template. Must return a dictionary.
        """
        return {}

    def get(self, request, *args, **kwargs):
        if 'runjob' not in request.GET:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        rj_uuid = request.GET['runjob']
        runjob = get_object_or_404(RunJob, pk=(rj_uuid))

        sequence = runjob.workflow_job.sequence
        page = runjob.page

        # if this is the first job in the sequence, the file path is just the original image
        if sequence == 1:
            image_source = runjob.page
        else:
            previous_run_job = RunJob.objects.get(workflow_job__sequence=(sequence - 1),
                                                  workflow_run__uuid=runjob.workflow_run.uuid,
                                                  page = page.uuid)
            image_source = Result.objects.get(run_job__uuid=previous_run_job.uuid)

        self.data.update({'form_url': self.view_url,
                      'run_job_uuid': rj_uuid,
                      'image_source': image_source})

        self.data.update(self.runjob_context(runjob, request))

        for setting in runjob.job_settings:
            self.data[setting['name']] = setting['default']

        return render(request, "{0}/{1}".format('jobs', self.template_name), self.data)

    def post(self, request, *args, **kwargs):
        if 'run_job_uuid' not in request.POST:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        rj_uuid = request.POST['run_job_uuid']
        runjob = RunJob.objects.get(uuid=rj_uuid)

        for job_setting in runjob.job_settings:
            if job_setting['name'] in request.POST:
                job_setting['default'] = request.POST[job_setting['name']]

        runjob.needs_input = False
        runjob.save()

        return render(request, 'jobs/job_input_done.html')

class PolyMaskView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/poly_mask/"
        self.template_name = "poly_mask.html"
        return super(PolyMaskView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PolyMaskView, self).post(request, *args, **kwargs)

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

class NeonView(RodanInteractiveBaseView):
    try:
        from rodan.jobs.neon.utils import live_mei_url, compressed_image_url
        from rodan.jobs.neon import neon_handler
    except ImportError as e:
        print "Neon is not installed. Skipping interactive neon view."
        print "Exception:", e

    else:
        view_url = "/interactive/neon/"
        template_name = "neon.html"
        live_mei_url = staticmethod(live_mei_url)
        compressed_image_url = staticmethod(compressed_image_url)

        data = {'force_width': 1000, 'neume_library': 'salzinnes'  # This can be a setting
                }

        def runjob_context(self, runjob, request):
            return {'live_mei_url': os.path.join(request.get_host(), self.live_mei_url(runjob)),
                    'neon_handler_path': 'edit/' + str(runjob.uuid),
                    'edit_title': 'Runjob ' + str(runjob.uuid),
                    'neon_image': os.path.join(request.get_host(),
                                                           self.compressed_image_url(runjob))}

class PixelSegmentView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/pixel_segment/"
        self.template_name = "pixel_segment.html"
        return super(PixelSegmentView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PixelSegmentView, self).post(request, *args, **kwargs)
