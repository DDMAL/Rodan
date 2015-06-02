from PIL import Image, ImageOps, ImageEnhance
from rodan.jobs.base import RodanTask

class RedFilter(RodanTask):
    name = "PRF.red_filtering"
    author = "Rivu Khoda & Yihong Lui"
    description = "Filters a spectrum of red color from image" 
    settings = {} 
    enabled = True
    category = "Filter"
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
        sal = Image.open(inputs['input'][0]['resource_path'])
        ImageOps.autocontrast(sal, 0)
		 
        red_layer = sal.split()[0]
        # red_layer.save('compat_redlayer.png')
        notes = red_layer.point(lambda i: i > 120 and 255).convert('1')
        notes.save(outputs['Staffless Image'][0]['resource_path'], "PNG")
		 
        for x in range(0, sal.size[0]):
	        for y in range(0, sal.size[1]):
	            if sal.getpixel((x, y)) == (255, 255, 255):
		        sal.putpixel((x, y), (0, 0, 0))

        enhancer = ImageEnhance.Color(sal)
        enh_red_layer = enhancer.enhance(4).split()[0]
        staff = enh_red_layer.point(lambda i: i < 255 and 255).convert('1')
		 
        staff.save(outputs['Neumeless Image'][0]['resource_path'], "PNG")





