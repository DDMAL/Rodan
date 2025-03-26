from rodan.jobs.base import RodanTask
import cv2
import numpy as np
import math
from PIL import Image
import json
import json.encoder

def dist(pt1, pt2):
    return math.sqrt(((pt1[0] - pt2[0])**2) + ((pt1[1] - pt2[1])**2))

def coords(x1, y1, x2, y2, new_x):
    slope = (y2 - y1) / (x2 - x1)
    b = (-1 * (slope * x1)) + y1
    return (slope * new_x) + b

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
            }
        },
        "staves": staves
    }

class AquitanianReferenceLineFinding(RodanTask):
    name = "Aquitanian Reference Line Finding"
    author = "Deanna Chun"
    description = "Trace single Aquitanian reference lines"
    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'Python3',
        'required': ['Slices'],
        'properties': {
            'Slices': {
                'type': 'integer',
                'default': 8,
                'minimum': 1,
                'maximum': 24,
                'description': 'Number of divisions per single reference line'
            }
        }
    }
    enabled = True
    category = "Staff Detection"
    interactive = False
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
    },
    {
        'name': 'Overlayed Lines',
        'resource_types': ['image/rgb+png'],
        'minimum': 0,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        input_path = inputs["Image containing staves (RGB, greyscale, or onebit)"][0]["resource_path"]
        overlay = "Overlayed Lines" in outputs
        slices = settings['Slices']
        
        img = cv2.imread(input_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
                img_sect = img[y:y+h, x+(part*i):x+(part*(i+1))]
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
                    if overlay:
                        cv2.line(img, tuple(line[0]), tuple(line[1]), (255, 0, 0), 2)
            ret.append(([x, y, w, h], lines))

        jsomr = to_json(img, ret)

        outfile_path = outputs['JSOMR'][0]['resource_path']
        with open(outfile_path, "w") as outfile:
            outfile.write(json.dumps(jsomr))
        
        if overlay:
            outfile_path2 = outputs["Overlayed Lines"][0]["resource_path"]
            #img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            overlay_save = Image.fromarray(img)
            overlay_save.save(outfile_path2, 'PNG')

        return True