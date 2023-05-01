from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from rodan.jobs.base import RodanTask

class RedFilter(RodanTask):
    name = "Red filtering"
    author = "Rivu Khoda & Yihong Luo"
    description = "Filters a spectrum of red color from image" 
    settings = {'job_queue': 'Python3'}
    enabled = True
    category = "PIL - Filter"
    interactive = False
    
    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/rgb+png'], 
        'minimum': 1,
        'maximum': 1
    }]  
    output_port_types = [{
        'name':'Neumeless Image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1 
    }, {
        'name': 'Staffless Image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        sal = Image.open(inputs['input'][0]['resource_path']).convert("RGB")
        ImageOps.autocontrast(sal, 0)
         
        red_layer = sal.split()[0]
        # red_layer.save('compat_redlayer.png')
        notes = red_layer.point(lambda i: i > 120 and 255).convert('1')
        notes.save(outputs['Staffless Image'][0]['resource_path'], "PNG")
         
        sal_np = np.asarray(sal)
        sal_np_mask = np.all(sal_np==255, axis=-1)
        results = np.where(sal_np_mask==True) # Get the x,y positions of (255, 255, 255)
        for x, y in zip(results[0], results[1]): # Replace them with (0, 0, 0)
            sal.putpixel((x, y), (0, 0, 0))

        enhancer = ImageEnhance.Color(sal)
        enh_red_layer = enhancer.enhance(4).split()[0]
        staff = enh_red_layer.point(lambda i: i < 255 and 255).convert('1')
         
        staff.save(outputs['Neumeless Image'][0]['resource_path'], "PNG")

    def test_my_task(self, testcase):
        import cv2
        input_path = "/code/Rodan/rodan/test/files/CF-005.png"
        staffless_path = "/code/Rodan/rodan/test/files/CF-005_Staffless-Image.png"
        neumeless_path = "/code/Rodan/rodan/test/files/CF-005_Neumeless-Image.png"
        inputs = {
            "input": [
                { "resource_path":input_path }
            ]
        }
        outputs = {
            "Staffless Image": [
                { "resource_path":testcase.new_available_path() }
            ],
            "Neumeless Image": [
                { "resource_path":testcase.new_available_path() }
            ]
        }
        settings = {}
        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The staffless image should be identical to the testcase
        in_staffless = cv2.imread(staffless_path, cv2.IMREAD_UNCHANGED)
        out_staffless = cv2.imread(outputs["Staffless Image"][0]["resource_path"], cv2.IMREAD_UNCHANGED)
        np.testing.assert_array_equal(in_staffless, out_staffless)
        del in_staffless, out_staffless

        # The neumeless image should be identical to the testcase
        in_neumeless = cv2.imread(neumeless_path, cv2.IMREAD_UNCHANGED)
        out_neumeless = cv2.imread(outputs["Neumeless Image"][0]["resource_path"], cv2.IMREAD_UNCHANGED)
        np.testing.assert_array_equal(in_neumeless, out_neumeless)
        del in_neumeless, out_neumeless