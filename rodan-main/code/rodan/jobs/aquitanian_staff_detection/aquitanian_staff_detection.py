from rodan.jobs.base import RodanTask
import cv2
import numpy as np
import math
from PIL import Image

def dist(pt1, pt2):
    return math.sqrt(((pt1[0] - pt2[0])**2) + ((pt1[1] - pt2[1])**2))

def points(p1, p2, width):
    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]

    m = (y2 - y1) / (x2 - x1)

    b = (-1 * (m * x1)) + y1
    y3 = (m * width) + b

    return [int(b), int(y3)]

def coords(x1, y1, x2, y2, new_x):
    slope = (y2 - y1) / (x2 - x1)
    b = (-1 * (slope * x1)) + y1
    return (slope * new_x) + b

def remove_transparent(i):
    t_mask = i[:, :, 3] == 0
    i[t_mask] = [255, 255, 255, 255]
    return cv2.cvtColor(i, cv2.COLOR_BGRA2BGR)

class StrikethroughStaffDetection(RodanTask):
    name = "Strikethrough Aquitanian Staff Detection"
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

        #keep lines that aren't too close together - about one per staff line and the straightest line
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

        #plot points
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

        if overlay:
            outfile_path2 = outputs["Overlayed Lines"][0]["resource_path"]
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            overlay_save = Image.fromarray(img)
            overlay_save.save(outfile_path2, 'PNG')
        
        return True
    
class UnderlineStaffDetection(RodanTask):
    name = "Underline Aquitanian Staff Detection"
    author = "Deanna Chun"
    description = "Underlines lines between lyrics to find the middle staff line"
    settings = {}
    enabled = True
    category = "Staff Detection"
    interactive = False
    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgba+png'],
        'minimum': 1,
        'maximum': 1
    },
    {
        'name': 'Original Page',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgba+png'],
        'minimum': 0,
        'maximum': 1
    }]

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
    },
    {
        'name': 'Overlayed Image',
        'resource_types': ['image/rgb+png'],
        'minimum': 0,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        input_path = inputs["PNG image"][0]["resource_path"]
        input_page = ""
        has_original = "Original Page" in inputs
        if has_original:
            input_page_path = inputs["Original Page"][0]["resource_path"]
            input_page = cv2.imread(input_page_path)

        line_overlay = "Overlayed Lines" in outputs
        img_overlay = "Overlayed Image" in outputs

        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        remove_transparent(img)
        height, width, _ = img.shape
        blank = np.zeros((height, width, 3), np.uint8)

        #setup for finding bounding boxes
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 1))
        dilate = cv2.dilate(thresh, kernal, iterations=7)
        conts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        conts = conts[0] if len(conts) == 2 else conts[1]
        lines = []

        #convert bounding boxes to underlines
        for c in conts:
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            #sort by least to greatest y vals
            box = sorted(box, key=lambda x: x[1], reverse=True)

            #has to assume certain image sizes etc for thsi to work
            if dist(box[0], box[1]) < 40 and dist(box[0], box[1]) < dist(box[0], box[2]):
                lines.append([box[0], box[2]])
            else:
                lines.append([box[0], box[1]])

        groups = []

        #group together lines that are close enough in y value
        for line in lines:
            add = True
            for group in groups:
                for li in group:
                    if (abs(li[0][1] - line[0][1]) <= 30) or (abs(li[1][1] - line[1][1]) <= 30):
                        add = False
                        group.append(line)
                        break
            if add:
                groups.append([line])

        #find values to separate page into left column and right column
        left_col = 100000
        right_col = 0
        for group in groups:
            for pts in group:
                pts.sort(key=lambda x: x[0])
            group.sort(key=lambda x: x[0][0])
            if group[0][0][0] < left_col:
                left_col = group[0][0][0]
            if group[-1][1][0] > right_col:
                right_col = group[-1][1][0]

        separator = int((left_col + right_col) / 2)
        cv2.line(blank, (left_col, 0), (left_col, 5000), (0, 0, 255))
        cv2.line(blank, (separator, 0), (separator, 5000), (0, 0, 0))
        cv2.line(blank, (right_col, 0), (right_col, 5000), (0, 255, 0))

        if line_overlay:
            cv2.line(img, (left_col, 0), (left_col, 5000), (0, 0, 255))
            cv2.line(img, (separator, 0), (separator, 5000), (0, 0, 0))
            cv2.line(img, (right_col, 0), (right_col, 5000), (0, 255, 0))

        if img_overlay and has_original:
            cv2.line(input_page, (left_col, 0), (left_col, 5000), (0, 0, 255))
            cv2.line(input_page, (separator, 0), (separator, 5000), (0, 0, 0))
            cv2.line(input_page, (right_col, 0), (right_col, 5000), (0, 255, 0))
        
        #separate groups into left/right sides
        groups_2 = []


        for group in groups:
            left = []
            right = []
            for pts in group:
                leftmost = pts[0][0]
                rightmost = pts[1][0]
                if leftmost - separator < 0 or abs(rightmost - separator) < 40:
                    left.append(pts)
                else:
                    right.append(pts)
            groups_2.append(left)
            groups_2.append(right)

        for k in range(0, len(groups_2)):
            group = groups_2[k]
            for n in range(0, len(group)):
                pts = group[n]
                pt1 = pts[0]
                pt2 = pts[1]
                if len(group) == 1:
                    separator_pt = [separator, int(coords(pt1[0], pt1[1], pt2[0], pt2[1], separator))]
                    if k % 2 == 0:
                        left_pt = [left_col, int(coords(pt1[0], pt1[1], pt2[0], pt2[1], left_col))]
                        group[n] = [left_pt, separator_pt]
                    else:
                        right_pt = [right_col, int(coords(pt1[0], pt1[1], pt2[0], pt2[1], right_col))]
                        group[n] = [separator_pt, right_pt]
                else:
                    for j in range(0, len(group) - 1):
                        pts = group[j]
                        pt1 = pts[0]
                        pt2 = pts[1]
                        next_pts = group[j+1]
                        next_pt1 = next_pts[0]
                        next_pt2 = next_pts[1]
                        if k % 2 == 0:
                            if j == 0:
                                new_left = [left_col, int(coords(pt1[0], pt1[1], pt2[0], pt2[1], left_col))]
                                group[j] = [new_left, pt2]
                                pt1 = new_left
                            if dist(pt1, pt2) > dist(next_pt1, next_pt2):
                                new_right = [next_pt1[0], int(coords(pt1[0], pt1[1], pt2[0], pt2[1], next_pt1[0]))]
                                group[j] = [pt1, new_right]
                                pt2 = new_right
                            else:
                                new_left = [pt2[0], int(coords(next_pt1[0], next_pt1[1], next_pt2[0], next_pt2[1], pt2[0]))]
                                group[j+1] = [new_left, next_pt2]
                                next_pt1 = new_left
                            if j == (len(group) - 2):
                                new_right = [separator, int(coords(next_pt1[0], next_pt1[1], next_pt2[0], next_pt2[1], separator))]
                                group[j+1] = [next_pt1, new_right]
                        else:
                            if j == 0:
                                new_left = [separator, int(coords(pt1[0], pt1[1], pt2[0], pt2[1], separator))]
                                group[j] = [new_left, pt2]
                                pt1 = new_left
                            if dist(pt1, pt2) > dist(next_pt1, next_pt2):
                                new_right = [next_pt1[0], int(coords(pt1[0], pt1[1], pt2[0], pt2[1], next_pt1[0]))]
                                group[j] = [pt1, new_right]
                                pt2 = new_right
                            else:
                                new_left = [pt2[0], int(coords(next_pt1[0], next_pt1[1], next_pt2[0], next_pt2[1], pt2[0]))]
                                group[j+1] = [new_left, next_pt2]
                                next_pt1 = new_left
                            if j == (len(group) - 2):
                                new_right = [right_col, int(coords(next_pt1[0], next_pt1[1], next_pt2[0], next_pt2[1], right_col))]
                                group[j+1] = [next_pt1, new_right]
                        

        #filter out empty lists
        lefts = []
        rights = []
        for n in range(0, len(groups_2)):
            group = groups_2[n]
            if n % 2 == 0:
                if not (group == []):
                    lefts.append(group)
            else:
                if not (group == []):
                    rights.append(group)
        lefts = sorted(lefts, key=lambda x: x[0][0][1])
        rights = sorted(rights, key=lambda x: x[0][0][1])

        #expand lines to edges
        for n in range(0, len(lefts) - 1):
            top = lefts[n]
            bottom = lefts[n+1]
            t_idx = 0
            b_idx = 0
            while b_idx < len(bottom):
                b_pts = bottom[b_idx]
                t_pts = top[t_idx]
                mid_l = (b_pts[0][0], int((b_pts[0][1] + t_pts[0][1]) / 2))
                mid_r = (b_pts[1][0], int((b_pts[1][1] + t_pts[1][1]) / 2))

                cv2.line(blank, mid_l, mid_r, (255, 0, 0), 2)
                if line_overlay:
                    cv2.line(img, mid_l, mid_r, (255, 0, 0), 2)
                if img_overlay and has_original:
                    cv2.line(input_page, mid_l, mid_r, (255, 0, 0), 2)
                if b_pts[1][0] > t_pts[1][0]:
                    t_idx += 1
                b_idx += 1

        # draw midpoints
        for n in range(0, len(rights) - 1):
            top = rights[n]
            bottom = rights[n+1]
            t_idx = 0
            b_idx = 0
            while b_idx < len(bottom):
                b_pts = bottom[b_idx]
                t_pts = top[t_idx]
                mid_l = (b_pts[0][0], int((b_pts[0][1] + t_pts[0][1]) / 2))
                mid_r = (b_pts[1][0], int((b_pts[1][1] + t_pts[1][1]) / 2))
                cv2.line(blank, mid_l, mid_r, (255, 0, 0), 2)
                if line_overlay:
                    cv2.line(img, mid_l, mid_r, (255, 0, 0), 2)
                if img_overlay and has_original:
                    cv2.line(input_page, mid_l, mid_r, (255, 0, 0), 2)
                if b_pts[1][0] > t_pts[1][0]:
                    t_idx += 1
                b_idx += 1

        for group in groups_2:
            for pts in group:
                cv2.line(blank, tuple(pts[0]), tuple(pts[1]), (0,0,255), 2)
                if line_overlay:
                    cv2.line(img, tuple(pts[0]), tuple(pts[1]), (0,0,255), 2)
                if has_original and img_overlay:
                    cv2.line(input_page, tuple(pts[0]), tuple(pts[1]), (0,0,255), 2)

        #save images
        blank_path = outputs["Lines"][0]["resource_path"]
        blank_save = Image.fromarray(blank)
        blank_save.save(blank_path, 'PNG')

        if line_overlay:
            line_path = outputs["Overlayed Lines"][0]["resource_path"]
            line_save = Image.fromarray(img)
            line_save.save(line_path, 'PNG')
        
        if img_overlay:
            img_path = outputs["Overlayed Image"][0]["resource_path"]
            if has_original:
                overlay_save = Image.fromarray(input_page)
                overlay_save.save(img_path, 'PNG')
            else:
                blank_save.save(img_path, 'PNG')










        


