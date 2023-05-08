from shutil import copyfile

from rodan.jobs.base import RodanTask


class GameraXMLDistributor(RodanTask):
    name = "GameraXML Distributor"
    author = "Andrew Fogarty"
    description = "Distribute a GameraXML file."
    settings = {'job_queue': 'Python3'}
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

    def test_my_task(self, testcase):
        input_path = "/code/Rodan/rodan/test/files/Interactive_Classifier_GameraXML_TrainingData.xml"
        output_path = testcase.new_available_path()
        gt_output_path = input_path
        inputs = {
            "GameraXML File": [{"resource_path":input_path}]
        }
        outputs = {
            "GameraXML File": [{"resource_path":output_path}]
        }
        settings = {
        }
        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))
        # also each line should be identical to its counterpart
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))