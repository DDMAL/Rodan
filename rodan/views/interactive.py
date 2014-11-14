import json
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.response import Response
from rodan.models import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.jobs.master_task import master_task


class InteractiveView(View):
    """
    Rodan makes available interfaces for interactive jobs. Each endpoint accepts
    GET and POST requests. An exception is Neon, which has its own API (and is
    discussed elsewhere).

    #### Parameters
    - `interface` -- GET-only (optional). Specify the name of interface. If not
      provided, the API will return a list of accepted interfaces in JSON format.
    - `run_job` -- GET & POST. UUID of the associated RunJob.
    - `**kwargs` -- POST-only. Job settings.
    """
    def get(self, request, run_job_uuid):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.workflow_run.cancelled:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        # Read directive
        directive_path = runjob.inputs.filter(input_port__input_port_type__name='directive').first().resource.compat_resource_file.path
        with open(directive_path, 'r') as f:
            directive = json.load(f)

        # Return which interfaces are supported, if param 'interface' is not provided.
        if 'interface' not in request.GET:
            supported_interfaces = map(lambda d: d['name'], directive['acceptable_interfaces'])
            return Response(supported_interfaces, content_type='application/json')

        # Verify interface
        interface_configuration = filter(lambda d: d['name'] == request.GET['interface'], directive['acceptable_interfaces'])
        if not interface_configuration:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        # Go!
        resource_obj = runjob.inputs.filter(input_port__input_port_type__name='resource').first().resource
        context = {'run_job': rj_uuid,
                   'resource_obj': resource_obj,
                   'kwargs': interface_configuration['kwargs']}
        template_name = 'jobs/{0}.html'.format(interface_configuration['name'])
        return render(request, template_name, context)


    def post(self, request, run_job_uuid):
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.workflow_run.cancelled:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)
        if not runjob.needs_input or not runjob.ready_for_input:
            return render(request, 'jobs/bad_request.html', status=status.HTTP_400_BAD_REQUEST)

        d = {}
        for k, v in request.POST.iteritems():
            d[k] = v

        runjob.needs_input = False
        runjob.ready_for_input = False
        runjob.status = RunJobStatus.HAS_FINISHED
        runjob.error_summary = ''
        runjob.error_details = ''
        runjob.save()
        resource = runjob.outputs.first().resource
        resource.compat_resource_file.save('', ContentFile(json.dumps(d)))

        # call master_task to continue workflowrun
        master_task.apply_async((runjob.workflow_run.uuid,))

        return render(request, 'jobs/job_input_done.html')

"""
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


class PixelSegmentView(RodanInteractiveBaseView):
    def get(self, request, *args, **kwargs):
        self.view_url = "/interactive/pixel_segment/"
        self.template_name = "pixel_segment.html"
        return super(PixelSegmentView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(PixelSegmentView, self).post(request, *args, **kwargs)
"""
