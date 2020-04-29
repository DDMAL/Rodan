from rodan.jobs.base import RodanTask
from rodan.models import Input, ResourceLabel
from django.conf import settings as rodan_settings

import re


class Labeler(RodanTask):
    name = 'Labeler'
    author = 'Juliette Regimbal'
    description = 'Add a label to resources'
    settings = {
        'title': 'Parameters',
        'type': 'object',
        'job_queue': 'celery',
        'properties': {
            'Label': {
                'type': 'string',
                'default': 'marked'
            }
        }
    }
    enabled = True
    category = 'Utility'
    interactive = False

    input_port_types = [
        {
            'name': 'Resource',
            'minimum': 1,
            'maximum': 1,
            'resource_types': lambda mime: re.match("^[-\w]+/[-\w+]+$", mime)
        }
    ]

    output_port_types = []

    def _inputs(self, runjob, with_urls=False):
        """
        Return a dictionary of list of input file path and input resource type.
        If with_urls=True, it also includes the resource url and thumbnail urls.
        """

        def _extract_resource(resource, resource_type_mimetype=None):
            r = {
                # convert 'unicode' object to 'str' object for consistency
                "resource_path": str(resource.resource_file.path),
                "resource_type": str(
                    resource_type_mimetype or resource.resource_type.mimetype
                ),
                "resource": resource,
            }
            if with_urls:
                r["resource_url"] = str(resource.resource_url)
                r["diva_object_data"] = str(resource.diva_json_url)
                r["diva_iip_server"] = getattr(rodan_settings, "IIPSRV_URL")
                r["diva_image_dir"] = str(resource.diva_image_dir)
            return r

        input_objs = (
            Input.objects.filter(run_job=runjob)
            .select_related("resource", "resource__resource_type", "resource_list")
            .prefetch_related("resource_list__resources")
        )

        inputs = {}
        for input in input_objs:
            ipt_name = str(input.input_port_type_name)
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            if input.resource is not None:  # If resource
                inputs[ipt_name].append(_extract_resource(input.resource))
            elif input.resource_list is not None:  # If resource_list
                inputs[ipt_name].append(
                    map(
                        lambda x: _extract_resource(
                            x, input.resource_list.get_resource_type().mimetype
                        ),
                        input.resource_list.resources.all(),
                    )
                )
            else:
                raise RuntimeError(
                    (
                        "Cannot find any resource or resource list on Input" " {0}"
                    ).format(input.uuid)
                )
        return inputs

    def run_my_task(self, inputs, settings, outputs):
        label = None
        try:
            label = ResourceLabel.objects.get(name=settings['Label'])
        except ResourceLabel.DoesNotExist:
            label = ResourceLabel(name=settings['Label'])
            label.save()
        inputs['Resource'][0]['resource'].labels.add(label)
