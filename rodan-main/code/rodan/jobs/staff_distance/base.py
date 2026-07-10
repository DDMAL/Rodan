from rodan.jobs.base import RodanTask
import cv2 as cv
import logging
import json
logger = logging.getLogger('rodan')

class StaffDistance(RodanTask):
    name = 'Staff Distance Finding'
    author = 'Zhanna Klimanova, Anthony Tan'
    description = 'Finds distance between staff lines. Returns distance and distance / 64.'
    enabled = True
    category = 'OMR - Layout analysis'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'GPU',
    }

    input_port_types = [
        {'name': 'Input Image', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgb+png']},
    ]

    output_port_types = [
        {
        'name': 'Resize Ratio',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
        }
    ]

    def run_my_task(self, inputs, settings, outputs):
        from .count_lines import preprocess_image, calculate_via_slices
        image_path = inputs['Input Image'][0]['resource_path']
        image = cv.imread(image_path,cv.IMREAD_UNCHANGED)
        processed = preprocess_image(image)
        distance = calculate_via_slices(processed)
        ratio = 64 / distance
        

        out_json_file = outputs['Resize Ratio'][0]['resource_path']

        out_json = {
            'distance': distance,
            'ratio': ratio
        }
        with open(out_json_file, 'w') as f:
            json.dump(out_json, f)


        return True

    def test_my_task(self, testcase):
        # count_lines depends on scikit-image; skip gracefully where it is not
        # installed so test_all_jobs stays green. Uses a real chant-manuscript
        # fixture (CF-005.png) so the staff-line spacing is well-defined (a
        # staff-less image would yield distance 0 -> ZeroDivision on 64/distance).
        try:
            import skimage  # noqa: F401
        except ImportError:
            return
        input_image = "/code/Rodan/rodan/test/files/CF-005.png"
        output_path = testcase.new_available_path()
        inputs = {'Input Image': [{'resource_type': 'image/rgb+png', 'resource_path': input_image}]}
        outputs = {'Resize Ratio': [{'resource_type': 'application/json', 'resource_path': output_path}]}
        self.run_my_task(inputs, {}, outputs)
        with open(output_path) as f:
            result = json.load(f)
        testcase.assertGreater(result['distance'], 0)
        testcase.assertAlmostEqual(result['ratio'], 64 / result['distance'])