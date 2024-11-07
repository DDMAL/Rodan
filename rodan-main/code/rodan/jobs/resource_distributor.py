__version__ = "1.0.0"
import shutil

from rodan.jobs.base import RodanTask
from rodan.models import ResourceType, Input, Output
from django.conf import settings as rodan_settings

import logging

logger = logging.getLogger("rodan")

def log_structure(data, level=0):
    if isinstance(data, dict):
        for key, value in data.items():
            logger.info("%sKey: %s", "    " * level, key)
            log_structure(value, level + 1)
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            logger.info("%sIndex %d:", "    " * level, idx)
            log_structure(item, level + 1)
    else:
        logger.info("%sValue: %s", "    " * level, data)


class ResourceDistributor(RodanTask):
    name = 'Resource Distributor'
    author = 'Nicky Mirfallah'
    description = 'Distributes the resource to output'
    settings = {
        'title': 'Resource Distributor setting',
        'type': 'object',
        'properties': {
            'Resource type': {
                'enum': list(map(lambda rt: str(rt.mimetype), ResourceType.objects.all())),
                'type': 'string',
                'default': 'image/rgba+png',
                'description': 'Specifies the eligible resource types for input'
            },
            'User custom prefix': {
                'type': 'string',
                'default': 'custom prefix - ',
                'description': 'User specified prefix (please also include space, hyphen, etc.)'
            },
            'User custom suffix': {
                'type': 'string',
                'default': '- custom suffix',
                'description': 'User specified suffix (please also include space, hyphen, etc.)'
            }
        }
    }
    enabled = True
    category = "Miscellaneous"
    interactive = False
    error_summary = ""
    error_details = ""

    input_port_types = (
        {
            'name': 'Resource input',
            'minimum': 1,
            'maximum': 1,
            'resource_types': map(lambda rt: str(rt.mimetype), ResourceType.objects.all())
        },
    )
    output_port_types = (
        {
            'name': 'Resource output',
            'minimum': 1,
            'maximum': 1,
            'resource_types': map(lambda rt: str(rt.mimetype), ResourceType.objects.all())
        },
    )


    def _inputs(self, runjob, with_urls=False):
        """
        Return a dictionary of list of input file path and input resource type.
        If with_urls=True, it also includes the resource url and thumbnail urls.
        """

        self.runjob = runjob

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
        # log_structure(inputs)
        input_type = inputs['Resource input'][0]['resource_type']
        input_resource = inputs['Resource input'][0]['resource']
        input_name = input_resource.name
        valid_input_type_num = settings['Resource type']
        valid_input_type = self.settings['properties']['Resource type']['enum'][valid_input_type_num]  # noqa
        if input_type != valid_input_type:
            self.my_error_information(
                None,
                (
                    "Mismatched input of type {0}. The input type in job setting is "
                    "{1}"
                ).format(input_type, valid_input_type)
            )
            return False
        prefix = settings["User custom prefix"]
        if not isinstance(prefix, str):
            self.my_error_information(
                None,
                ("User custom prefix can only be strings")
            )
            return False
        suffix = settings["User custom suffix"]
        if not isinstance(suffix, str):
            self.my_error_information(
                None,
                ("User custom suffix can only be strings")
            )
            return False
        new_name = prefix + input_name + suffix
        assert isinstance(new_name,str)
        
        input_resource.rename(new_name)
        input_resource.save(update_fields=["resource_file"])

        outfile_path = outputs['Resource output'][0]['resource_path']
        infile_path = inputs['Resource input'][0]['resource_path']

        shutil.copyfile(infile_path, outfile_path)
        return True

    def my_error_information(self, exc, traceback):
        self.error_summary = "Resource type not valid"
        self.error_details = traceback

    def test_my_task(self, testcase):
        import PIL.Image
        import numpy as np
        from rodan.models import Resource, ResourceType
        resource_types_list = list(map(lambda rt: str(rt.mimetype), ResourceType.objects.all()))
        from model_mommy import mommy        

        # Create a Resource instance using mommy
        resource_type, created = ResourceType.objects.get_or_create(mimetype="image/rgb+png")
        rc = mommy.make(Resource, resource_type=resource_type, name="test_filename")

        inputs = {
                    "Resource input": [
                        {
                            "resource_path": testcase.new_available_path(),
                            "resource_type": rc.resource_type.mimetype,
                            "resource": rc
                        }
                    ]
                }
        outputs = {
                    "Resource output": [
                        {
                            "resource_type": "image/rgb+png",
                            "resource_path": testcase.new_available_path()
                        }
                    ]
                }
        settings = {
                    "Resource type": resource_types_list.index("image/rgb+png"),
                    "User custom prefix": "test prefix - ",
                    "User custom suffix": "- test suffix"
                    }
        
        original_image = rc.name

        PIL.Image.new("RGB", size=(50, 50), color=(255, 0, 0)).save(inputs['Resource input'][0]['resource_path'], 'PNG')
        array_gt = np.zeros((50, 50, 3)).astype(np.uint8)
        array_gt[:, :, 0] = 255

        self.run_my_task(inputs, settings, outputs)

        result = PIL.Image.open(outputs['Resource output'][0]['resource_path'])
        array_result = np.asarray(result)

        # This jobs only moves an input resource to a new path, so the datatype (png) and data (array) should be identical.
        # The type (png) should stays the same
        testcase.assertEqual(result.format, 'PNG')
        # and the data should be identical
        np.testing.assert_equal(array_gt, array_result)

        # Test name change
        new_name = f"{settings['User custom prefix']}{original_image}{settings['User custom suffix']}"
        testcase.assertEqual(inputs['Resource input'][0]['resource'].name, new_name)