from rodan.jobs.base import RodanTask
try:
    from gamera.core import load_image, init_gamera
    from gamera import gamera_xml
    from .StaffFinding import StaffFinder
    from .PitchFinding import PitchFinder
    init_gamera()
except ImportError:
    pass

import sys
import json
import json.encoder

import cv2
import numpy as np
import math
from PIL import Image

def dist(pt1, pt2):
    return math.sqrt(((pt1[0] - pt2[0])**2) + ((pt1[1] - pt2[1])**2))

def coords(x1, y1, x2, y2, new_x):
    slope = (y2 - y1) / (x2 - x1)
    b = (-1 * (slope * x1)) + y1
    return (slope * new_x) + b

def to_json(img, data):
    h, w, _ = img.shape
    staves = []
    for i in range(0, len(data)):
        cur = data[i]
        box = cur[0]
        x, y, width, height = box
        lines = cur[1]
        staves.append({
            "staff_no": i,
            "bounding_box":{
                "ncols": width,
                "nrows": height,
                "ulx": x,
                "uly": y
            },
            "num_lines": 1,
            "line_positions": lines
        })
    return {
        "page":{
            "resolution": 0.0,
            "bounding_box":{
                "ncols": w,
                "nrows": h,
                "ulx": 0,
                "uly": 0
            },
            "staves": staves
        }
    }

def padding(sect):
    #add extra space around the line segments
    old_h, old_w, c = sect.shape
    new_h = old_h + 100
    new_w = old_w + 100
    result = np.full((new_h, new_w, c), (255, 255, 255), dtype=np.uint8)
    x_center = (new_w - old_w) // 2
    y_center = (new_h - old_h) // 2
    result[y_center:y_center+old_h, x_center:x_center+old_w] = sect

    #bounding rectangle preprocessing
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1, 1), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 1))
    dilate = cv2.dilate(thresh, kernal, iterations=7)
    conts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    conts = conts[0] if len(conts) == 2 else conts[1]
    conts = sorted(conts, key=lambda x: cv2.boundingRect(x)[0])

    ret = []

    for c in conts:
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        result = cv2.drawContours(result,[box],0,(0,255,0),2)
        origin = box[0]
        new_pts = sorted(box, key=lambda x: dist(x, origin))
        pt0 = new_pts[0]
        pt1 = new_pts[1]
        pt2 = new_pts[2]
        pt3 = new_pts[3]

        mid1 = [int((pt0[0] + pt1[0]) / 2) - 50, int((pt0[1] + pt1[1]) / 2) - 50]
        mid2 = [int((pt2[0] + pt3[0]) / 2) - 50, int((pt2[1] + pt3[1]) / 2) - 50]
        ret = [mid1, mid2]

    return ret

class MiyaoStaffinding(RodanTask):
    name = 'Miyao Staff Finding'
    author = 'Noah Baxter'
    description = 'Finds the location of staves in an image and returns them as a JSOMR file.'
    enabled = True
    category = 'aOMR'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'Python3',
        'required': ['Number of lines', 'Interpolation'],
        'properties': {
            'Number of lines': {
                'type': 'integer',
                'default': 4,
                'minimum': 0,
                'maximum': 8,
                'description': 'Number of lines within each staff. When zero, the number is automatically detected.'
            },
            'Interpolation': {
                'type': 'boolean',
                'default': True,
                'description': 'Interpolate found line points so all lines have the same number of points. This MUST be True for pitch finding to succeed.'
            },
            'Slices': {
                'type': 'integer',
                'default': 8,
                'minimum': 1,
                'maximum': 24,
                'description': '(For One Staff Finding) Number of divisions per staff line'
            }
        }
    }

    input_port_types = [{
        'name': 'Image containing staves (RGB, greyscale, or onebit)',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    output_port_types = [{
        'name': 'JSOMR',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):
        
        #Branch for one staff finding
        if settings['Number of lines'] == 1:
            image = cv2.imread(inputs['Image containing staves (RGB, greyscale, or onebit)'][0]['resource_path'])
            slices = settings['Slices']
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (1, 1), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 1))
            dilate = cv2.dilate(thresh, kernal, iterations=7)
            conts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            conts = conts[0] if len(conts) == 2 else conts[1]
            conts = sorted(conts, key=lambda x: cv2.boundingRect(x)[0])

            ret = []

            for c in conts:
                x, y, w, h = cv2.boundingRect(c)
                part = w // slices
                last = []
                lines = []
                for i in range(0, slices):
                    img_sect = image[y:y+h, x+(part*i):x+(part*(i+1))]
                    line = padding(img_sect)
                    if line != []:
                        line[0][0] += x+(part*i)
                        line[1][0] += x+(part*i)
                        line[0][1] += y
                        line[1][1] += y

                        #normalize lines to bounds
                        new_y1 = int(coords(line[0][0], line[0][1], line[1][0], line[1][1], x+(part*i)))
                        new_y2 = int(coords(line[0][0], line[0][1], line[1][0], line[1][1], x+(part*(i+1))))
                        line[0] = [x+(part*i), new_y1]
                        line[1] = [x+(part*(i+1)), new_y2]

                        #make sure lines connect together
                        if last != []:
                            line[0] = last
                        last = line[1]
                        lines.append(line[0])

                        #draw line

                ret.append(([x, y, w, h], lines))

            jsomr = to_json(image, ret)

            outfile_path = outputs['JSOMR'][0]['resource_path']
            with open(outfile_path, "w") as outfile:
                outfile.write(json.dumps(jsomr))
            return True


        # Inputs
        image = load_image(inputs['Image containing staves (RGB, greyscale, or onebit)'][0]['resource_path'])
        kwargs = {
            'lines_per_staff': settings['Number of lines'],
            'staff_finder': 0,          # 0 for miyao
            'binarization': 1,
            'interpolation': settings['Interpolation'],
        }

        sf = StaffFinder(**kwargs)

        page = sf.get_page_properties(image)
        staves = sf.get_staves(image)

        jsomr = {
            'page': page,
            'staves': staves,
        }

        # Outputs
        outfile_path = outputs['JSOMR'][0]['resource_path']
        with open(outfile_path, "w") as outfile:
            outfile.write(json.dumps(jsomr))

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_dilate_png_path = "/code/Rodan/rodan/test/files/ms73-068_dilate_output.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/ms73-068-miyao-staff-finding.json"
        inputs = {
            "Image containing staves (RGB, greyscale, or onebit)": [{"resource_path":input_dilate_png_path}]
        }
        outputs = {
            "JSOMR": [{"resource_path":output_path}]
        }
        settings = {'Number of lines': 4, 'Interpolation': True}

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


class HeuristicPitchFinding(RodanTask):
    name = 'Heuristic Pitch Finding'
    author = 'Noah Baxter'
    description = 'Calculates pitch values for Classified Connected Componenets from a JSOMR containing staves, and returns the results as a JSOMR file'
    settings = {
        'title': 'aOMR settings',
        'type': 'object',
        'job_queue': 'Python3',

        'required': ['Discard Size'],
        'properties': {
            'Discard Size': {
                'type': 'integer',
                'default': 12,
                'minimum': 5,
                'maximum': 25,
                'description': '',
            },
        }
    }
    enabled = True
    category = 'aOMR'
    interactive = False
    input_port_types = [{
        'name': 'JSOMR of staves and page properties',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    },
        {
        'name': 'GameraXML - Classified Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]
    output_port_types = [{
        'name': 'JSOMR of glyphs, staves, and page properties',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):

        # Inputs
        infile_path = inputs['JSOMR of staves and page properties'][0]['resource_path']
        with open(infile_path, 'r') as infile:
            jsomr_string = infile.read()

        jsomr = json.loads(jsomr_string)
        glyphs = gamera_xml.glyphs_from_xml(inputs['GameraXML - Classified Connected Components'][0]['resource_path'])

        kwargs = {
            'discard_size': settings['Discard Size'],
        }

        pf = PitchFinder(**kwargs)

        page = jsomr['page']
        staves = jsomr['staves']
        pitches = pf.get_pitches(glyphs, staves)

        # Outputs
        jsomr = {
            'page': page,
            'staves': staves,
            'glyphs': pitches,
        }
        #jsomr = json.decoder(jsomr)


        def rec_serialize(byte2str):
 
            """
            A recursive function that iterates over a JSON object and changes all the bytes values to string
            """
            # dealing with dictionaries and lists and other stuff as three categories
            if type(byte2str) == list:
                # recursively for all elements 
                for index in range(len(byte2str)):
                    element = byte2str[index]
                    byte2str[index] = rec_serialize(element)

            elif type(byte2str) == dict:
                for key in byte2str:
                    value = byte2str[key]
                    byte2str[key] = rec_serialize(value)
            elif type(byte2str) == bytes:
                # the element must be decoded
                return byte2str.decode("UTF-8")

            return byte2str

        outfile_path = outputs['JSOMR of glyphs, staves, and page properties'][0]['resource_path']
        
        with open(outfile_path, "w") as outfile:
            serialized = rec_serialize(jsomr)
            r = json.dumps(serialized)
            outfile.write(r)

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_nic_path = "/code/Rodan/rodan/test/files/238r-nic.xml"
        input_staff_finding_path = "/code/Rodan/rodan/test/files/238r-miyao-staff-finding.json"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/238r-heuristic_pitch_finding.json"

        inputs = {
            "JSOMR of staves and page properties": [{"resource_path":input_staff_finding_path}],
            "GameraXML - Classified Connected Components": [{"resource_path":input_nic_path}]
        }
        outputs = {
            "JSOMR of glyphs, staves, and page properties": [{"resource_path":output_path}]
        }
        settings = {'Discard Size': 12}

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
