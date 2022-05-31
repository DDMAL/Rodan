from shutil import copyfile

from rodan.jobs.base import RodanTask


class GameraXMLDistributor(RodanTask):
    name = "GameraXML Distributor"
    author = "Andrew Fogarty"
    description = "Distribute a GameraXML file."
    settings = {}
    enabled = True
    category = "Resource Distributor"
    interactive = False
    input_port_types = [
        {
            "name": "GameraXML File",
            "resource_types": ["application/gamera+xml"],
            "minimum": 1,
            "maximum": 1,
            "is_list": False
        }
    ]
    output_port_types = [
        {
            "name": "GameraXML File",
            "resource_types": ["application/gamera+xml"],
            "minimum": 1,
            "maximum": 1,
            "is_list": False
        }
    ]

    def run_my_task(self, inputs, settings, outputs):
        copyfile(inputs['GameraXML File'][0]['resource_path'],
                 outputs['GameraXML File'][0]['resource_path'])
        return True
