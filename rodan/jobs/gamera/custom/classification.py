import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from gamera.core import load_image

from rodan.jobs.base import RodanTask


class ClassificationTask(RodanTask):
    name = 'gamera.custom.classification'
    author = "Ling-Xiao Yang"
    description = "Performs classification on a binarized staff-less image and outputs an xml file"
    enabled = True
    category = "Classifier"
    settings = {}
    interactive = False

    input_port_types = [{
        'name': 'Staffless Image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'Classifier',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'Feature Selection',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Classification Result',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        staffless_image_path = inputs['Staffless Image'][0]['resource_path']
        classifier_path = inputs['Classifier'][0]['resource_path']
        selection_path = inputs['Feature Selection'][0]['resource_path']
        result_path = outputs['Classification Result'][0]['resource_path']

        cknn = gamera.knn.kNNNonInteractive(classifier_path, 'all', True, 1)
        cknn.load_settings(selection_path)
        func = gamera.classify.BoundingBoxGroupingFunction(4)
        input_image = gamera.core.load_image(staffless_image_path)
        ccs = input_image.cc_analysis()

        cs_image = cknn.group_and_update_list_automatic(ccs,
                                                        grouping_function=func,
                                                        max_parts_per_group=4,
                                                        max_graph_size=16)

        cknn.generate_features_on_glyphs(cs_image)
        output_xml = gamera.gamera_xml.WriteXMLFile(glyphs=cs_image, with_features=True)
        output_xml.write_filename(result_path)
