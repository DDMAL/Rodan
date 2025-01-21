from rodan.jobs.base import RodanTask
import cv2
import numpy as np
from PIL import Image

def points(p1, p2, width):
    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]

    m = (y2 - y1) / (x2 - x1)

    b = (-1 * (m * x1)) + y1
    y3 = (m * width) + b

    return [int(b), int(y3)]

class AquitanianStaffDetection(RodanTask):
    name = "Aquitanian Staff Detection"
    author = "Deanna Chun"
    description = "Uses lines between lyrics to find the middle staff line"
    settings = {}
    enabled = True
    category = "Staff Detection"
    interactive = False
    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgba+png'],
        'minimum': 1,
        'maximum': 1
    }]

    #can return image with lines overlayed or just the lines in theory
    output_port_types = [{
        'name': 'Lines',
        'resource_types': ['image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    },
    {
        'name': 'Overlayed Lines',
        'resource_types': ['image/rgb+png'],
        'minimum': 0,
        'maximum': 1
    }]


    def run_my_task(self, inputs, settings, outputs):
        input_path = inputs["PNG image"][0]["resource_path"]

        overlay = "Overlayed Lines" in outputs

        img = cv2.imread(input_path)
        height, width, _ = img.shape
        blank = np.zeros((height, width, 3), np.uint8)

        #use HoughLines to detect lines in the image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        can = cv2.Canny(gray, 10, 200)
        lines = cv2.HoughLines(can, 1, np.pi/180.0, 75, np.array([]))

        cur = []

        #keep lines that aren't too close together - about one per staff line
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            add = True

            ctr = 0
            for c in cur:
                y1a = c[1]
                y2a = c[3]
                if y1 > y1a and y2 < y2a:
                    add = False
                    break
                if y1 < y1a and y2 > y2a:
                    add = False
                    break
                if abs(y1 - y1a) < 30:
                    add = False
                    break
                if abs(y2 - y2a) < 30:
                    add = False
                    break
            if add:
                cur.append([x1, y1, x2, y2])

        cur = sorted(cur, key=lambda x: x[1])


        for c in cur:
            x1 = c[0]
            y1 = c[1]
            x2 = c[2]
            y2 = c[3]

            pts = points((x1, y1), (x2, y2), width)


            cv2.line(blank, (0, pts[0]), (width, pts[1]), (0, 0, 255), 1)
            if overlay:
                cv2.line(img, (0, pts[0]), (width, pts[1]), (0, 0, 255), 1)
            ctr += 1


        for n in range(0, len(cur) - 1):
            c1 = cur[n]
            c2 = cur[n+1]
            # line a - lower line
            x1a = c1[0]
            y1a = c1[1]
            x2a = c1[2]
            y2a = c1[3]

            # line b - upper line
            y1b = c2[1]
            y2b = c2[3]

            mid1 = int((y1b + y1a) / 2)
            mid2 = int((y2b + y2a) / 2)

            pts = points((x1a, mid1), (x2a, mid2), width)


            cv2.line(blank, (0, pts[0]), (width, pts[1]), (255, 0, 0), 1)
            if overlay:
                cv2.line(img, (0, pts[0]), (width, pts[1]), (0, 0, 255), 1)

        outfile_path = outputs["Lines"][0]["resource_path"]
        blank_save = Image.fromarray(blank)
        blank_save.save(outfile_path, 'PNG')
        #cv2.imwrite(outfile_path + ".png", blank)

        if overlay:
            outfile_path2 = outputs["Overlayed Lines"][0]["resource_path"]
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            overlay_save = Image.fromarray(img)
            overlay_save.save(outfile_path2, 'PNG')

            #cv2.imwrite(outfile_path2 + ".png", img)
        
        return True


        


