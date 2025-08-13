from rodan.jobs.base import RodanTask
import cv2
import numpy as np
import math
from PIL import Image
import json
import json.encoder

#Helper function for distance formula
def dist(pt1, pt2):
    return math.sqrt(((pt1[0] - pt2[0])**2) + ((pt1[1] - pt2[1])**2))

#Helper function to find the matching y value given an x value and 2 points of a line
def coords(x1, y1, x2, y2, new_x):
    slope = (y2 - y1) / (x2 - x1)
    b = (-1 * (slope * x1)) + y1
    return (slope * new_x) + b

#Handles each line segment by adding extra space, drawing a bounding box, and drawing a line through the center
#Returns the 2 coords for the line
def process_section(sect):
    #add extra space around the line segments
    old_h, old_w, c = sect.shape
    new_h = old_h + 100
    new_w = old_w + 100
    result = np.full((new_h, new_w, c), (255, 255, 255), dtype=np.uint8)
    x_center = (new_w - old_w) // 2
    y_center = (new_h - old_h) // 2
    result[y_center:y_center+old_h, x_center:x_center+old_w] = sect

    #preprocess image, draw bounding box around
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1, 1), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 1))
    dilate = cv2.dilate(thresh, kernal, iterations=7)
    conts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    conts = conts[0] if len(conts) == 2 else conts[1]
    conts = sorted(conts, key=lambda x: cv2.boundingRect(x)[0])

    ret = []

    #draw line through the bounding box
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

#Convert results into a JSOMR format
#Each reference line has 5 lines: 2 ledger lines below, the original line, and 2 ledger lines above
def to_json(img, data, neume_size):
    h, w, _ = img.shape
    staves = []
    for i in range(0, len(data)):
        cur = data[i]
        box = cur[0]
        x, y, width, height = box
        lines = cur[1]
        up_ledger_2 = [[x[0], x[1] - (2 * neume_size)] for x in lines]
        up_ledger_1 = [[x[0], x[1] - neume_size] for x in lines]
        down_ledger_1 = [[x[0], x[1] + neume_size] for x in lines]
        down_ledger_2 = [[x[0], x[1] + (2 * neume_size)] for x in lines]
        staves.append({
            "staff_no": i+1,
            "bounding_box":{
                "ncols": width,
                "nrows": height + (4 * neume_size),
                "ulx": x,
                "uly": y - (2 * neume_size)
            },
            "num_lines": 1,
            "line_positions": [up_ledger_2, up_ledger_1, lines, down_ledger_1, down_ledger_2]
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
        'required': ['Slices', 'Step Size: Punctum Height * 3'],
        'properties': {
            'Slices': {
                'type': 'integer',
                'default': 8,
                'minimum': 1,
                'maximum': 24,
                'description': 'Number of divisions per single reference line'
            },
            'Step Size: Punctum Height * 3': {
                'type': 'integer',
                'default': 30,
                'minimum': 1,
                'maximum': 500,
                'description': "The step size is the distance between consecutive two notes, which is an interval of a second, without saying if it's major or minor. It equals three times the punctum height in pixels. This is used to generate ledger lines above and below the original line."
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

    # Overall Workflow
    # 1. Draw bounding boxes around each reference line
    # 2. Split each bounding box into a number of sections given by slices
    # 3. Add extra space around each line segment, then draws another bounding box (not necessarily rectangular)
    # 4. Draw a line through the center of the line segment bounding box
    # 5. Link each segment together
    # 6. After all lines are found, convert into JSOMR format
    def run_my_task(self, inputs, settings, outputs):
        input_path = inputs["Image containing staves (RGB, greyscale, or onebit)"][0]["resource_path"]
        overlay = "Overlayed Lines" in outputs
        slices = settings['Slices']
        
        img = cv2.imread(input_path)

        #Image preprocessing to set up bounding boxes
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (1, 1), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 1))
        dilate = cv2.dilate(thresh, kernal, iterations=7)
        conts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        conts = conts[0] if len(conts) == 2 else conts[1]
        conts = sorted(conts, key=lambda x: cv2.boundingRect(x)[0])

        ret = []

        #Split each bounding box into sections, then connect the line segments
        for c in conts:
            x, y, w, h = cv2.boundingRect(c)
            part = w // slices
            last = []
            lines = []
            for i in range(0, slices):
                img_sect = img[y:y+h, x+(part*i):x+(part*(i+1))]
                line = process_section(img_sect)
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

                    #make sure line segments connect together
                    if last != []:
                        line[0] = last
                    last = line[1]
                    lines.append(line[0])
                    if i == (slices - 1):
                        lines.append(line[1])
                    
                    #draw line
                    if overlay:
                        cv2.line(img, tuple(line[0]), tuple(line[1]), (255, 0, 0), 2)
            #save bounding box and line points
            ret.append(([x, y, w, h], lines))

        #sort staff lines based on y height
        ret = sorted(ret, key=lambda x: x[0][1])
        neume_size = settings['Step Size: Punctum Height * 3']

        #convert data into jsomr format
        jsomr = to_json(img, ret, neume_size)

        outfile_path = outputs['JSOMR'][0]['resource_path']
        with open(outfile_path, "w") as outfile:
            outfile.write(json.dumps(jsomr))
        
        if overlay:
            outfile_path2 = outputs["Overlayed Lines"][0]["resource_path"]
            overlay_save = Image.fromarray(img)
            overlay_save.save(outfile_path2, 'PNG')

        return True
