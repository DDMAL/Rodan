from gamera.core import ONEBIT
from gamera.toolkits import musicstaves

import copy


class StaffFinder(object):

    def __init__(self, **kwargs):

        self.lines_per_staff = kwargs['lines_per_staff']
        self.sfnd_algorithm = kwargs['staff_finder']
        self.binarization = kwargs['binarization']
        self.interpolation = kwargs['interpolation']

        # the results of the staff finder. Mostly for convenience
        self.staff_finder = None
        self.staves = None
        self.staff_bounds = None

        self.staff_results = {}

    ####################
    # Public Functions
    ####################

    def get_staves(self, image):

        if image.data.pixel_type != ONEBIT:
            image = self._binarize_image(image)

        s = self._get_staff_finding_algorithm(image, self.sfnd_algorithm)
        self._find_staves(s)
        self._process_staves()

        output = []
        # Fixes: Title page with no information bug
        if self.staves is None:
            return []

        for i, s in enumerate(self.staves):

            bounding_box = {
                'ncols': s['coords'][2] - s['coords'][0],
                'nrows': s['coords'][3] - s['coords'][1],
                'ulx': s['coords'][0],
                'uly': s['coords'][1],
            }

            cur_json = {
                'staff_no': s['staff_no'],
                'bounding_box': bounding_box,
                'num_lines': s['num_lines'],
                'line_positions': s['line_positions'],
            }

            output.append(cur_json)

        return output

    def get_page_properties(self, image):
        output = {
            # 'filename': image,
            'resolution': image.resolution,
            'bounding_box': {
                'ncols': image.ncols,
                'nrows': image.nrows,
                'ulx': 0,
                'uly': 0,
            }
        }

        return output

    def _binarize_image(self, image):
        image_resolution = image.resolution
        image = image.to_greyscale()
        bintypes = ['threshold',
                    'otsu_threshold',
                    'sauvola_threshold',
                    'niblack_threshold',
                    'gatos_threshold',
                    'abutaleb_threshold',
                    'tsai_moment_preserving_threshold',
                    'white_rohrer_threshold']
        image = getattr(image, bintypes[self.binarization])(0)
        # BUGFIX: sometimes an image loses its resolution after being binarized.
        if image.resolution < 1:
            image.resolution = image_resolution

        # check the amount of blackness of the image. If it's inverted,
        # the black area will vastly outweigh the white area.
        area = image.area().tolist()[0]
        black_area = image.black_area()[0]

        if area == 0:
            raise AomrError("Cannot divide by a zero area. Something is wrong.")

        # if greater than 70% black, invert the image.
        if (black_area / area) > 0.7:
            image.invert()

        return image

    def _get_staff_finding_algorithm(self, image, sfnd_alg):
        if sfnd_alg == 0:
            return musicstaves.StaffFinder_miyao(image)
        elif sfnd_alg is 1:
            return musicstaves.StaffFinder_dalitz(image)
        elif sfnd_alg is 2:
            return musicstaves.StaffFinder_projections(image)
        else:
            raise AomrStaffFinderNotFoundError("The staff finding algorithm was not found.")

    #################
    # Interpolation
    #################

    def _close_enough(self, y1, y2):
        val = 0.005     # y1 and y2 are within val% of each other
        valPix = 5      # best between 0 and 10

        # return (y1 > y2 * (1 - val) and y1 < y2 * (1 + val))      # proportional distance
        # return (y1 > y2 - valPix and y1 < y2 + valPix)            # linear distance
        return y1 == y2                                           # exact comparison

    def _find_left_pt(self, points, pos):
        if pos == 0:
            return False
        else:
            return pos - 1

    def _find_right_pt(self, points, pos):
        return next((i + pos + 1 for i, x in enumerate(points[pos + 1:]) if x[0]), False)

    def _generate_ref_line(self, staff):
        refLine = []

        for line in staff['line_positions']:
            for pt in line:
                pt = (pt[0], 0)     # remove all y values
                add = True

                if not refLine:
                    refLine.append(pt)
                    add = False         # initial point doesn't work the same way

                if refLine:
                    for l, rpt in enumerate(refLine):
                        if self._close_enough(rpt[0], pt[0]):
                            add = False
                            break

                if add:
                    inserted = False
                    for l, rpt in enumerate(refLine):
                        if pt[0] < rpt[0]:
                            refLine.insert(l, pt)
                            inserted = True
                            break

                    if not inserted:
                        refLine.append(pt)

        return refLine

    def _interpolate_staff_locations(self, staff_locations):
        interpolated_staves = copy.deepcopy(staff_locations)
        for i, staff in enumerate(interpolated_staves):

            refLine = self._generate_ref_line(staff)

            # interpolation based on refLine
            newSet = []
            for j, line in enumerate(staff['line_positions']):  # for each line
                newLine = [(False, False)] * len(refLine)  # generate line of false points with set length

                # put old values in correct spots
                nudge = 0
                for k, pt in enumerate(refLine):
                    # print k, '-', nudge, '=', k - nudge       # debug interpolating
                    if k - nudge < len(line) and self._close_enough(line[k - nudge][0], pt[0]):
                        newLine[k] = line[k - nudge]
                    else:
                        nudge += 1

                # for all missing points, interpolate
                for k, pt in enumerate(newLine):
                    if not pt[0]:

                        left = self._find_left_pt(newLine, k)
                        right = self._find_right_pt(newLine, k)

                        if not left:  # flat left
                            newLine[k] = refLine[k][0], newLine[right][1]

                        elif not right:  # flat right
                            newLine[k] = refLine[k][0], newLine[left][1]

                        else:
                            for l in range(k + 1, len(newLine)):
                                if newLine[l][0]:
                                    lowerY = newLine[k - 1][1]
                                    upperY = newLine[l][1]
                                    difY = upperY - lowerY
                                    den = l - k + 1.0

                                    for m in range(l - k):
                                        num = m + 1
                                        calc = lowerY + (difY * (num / den))
                                        newLine[k + m] = (refLine[k + m][0], int(calc))
                                    break

                newSet.append(newLine)
                # print '\n', "oldLine", len(line), line, '\n'
                # print "refLine", len(refLine), refLine, '\n'
                # print "newLine", len(newLine), newLine, '\n'

            interpolated_staves[i]['line_positions'] = newSet
        return interpolated_staves

    #################
    # Staff Finding
    #################

    def _find_staves(self, s):
        scanlines = 20
        blackness = 0.8
        tolerance = -1

        # there is no one right value for these things. We'll give it the old college try
        # until we find something that works.
        while not self.staff_finder:
            if blackness <= 0.3:
                # we want to return if we've reached a limit and still can't
                # find staves.
                return None

            s.find_staves(self.lines_per_staff, scanlines, blackness, tolerance)
            av_lines = s.get_average()
            if len(self._flatten(s.linelist)) == 0:
                # no lines were found
                return None

            # get a polygon object. This stores a set of vertices for x,y values along the staffline.
            self.staff_finder = s.get_polygon()

            if not self.staff_finder:
                lg.debug("No staves found. Decreasing blackness.")
                blackness -= 0.1

        # if len(self.staff_finder) < self.lines_per_staff:
        #     # the number of lines found was less than expected.
        #     return None

        all_line_positions = []

        for i, staff in enumerate(self.staff_finder):
            yv = []
            xv = []

            # linepoints is an array of arrays of vertices describing the
            # stafflines in the staves.
            #
            # For the staff, we end up with something like this:
            # [
            #   [ (x,y), (x,y), (x,y), ... ],
            #   [ (x,y), (x,y), (x,y), ... ],
            #   ...
            # ]
            line_positions = []

            for staffline in staff:
                pts = staffline.vertices
                yv += [p.y for p in pts]
                xv += [p.x for p in pts]
                line_positions.append([(p.x, p.y) for p in pts])

            ulx, uly = min(xv), min(yv)
            lrx, lry = max(xv), max(yv)

            # To accurately interpret objects above and below, we need to project
            # ledger lines on the top and bottom.
            #
            # Since we can't *actually* get the points, we'll predict based on the
            # first and last positions of the top and bottom lines.
            # first, get the top two and bottom two positions
            lines_top = line_positions[0:2]
            lines_bottom = line_positions[-2:]

            # find the start and end points for the existing lines:
            top_first_start_y = lines_top[0][0][1]
            top_first_end_y = lines_top[0][-1][1]

            top_second_start_y = lines_top[1][0][1]
            top_second_end_y = lines_top[1][-1][1]

            # find the average staff space by taking the start and end points
            # averaging the height.
            top_begin_height = top_second_start_y - top_first_start_y
            top_end_height = top_second_end_y - top_second_end_y

            average_top_space_diff = int(round((top_begin_height + top_end_height) * 0.5))
            imaginary_lines = []

            # take the second line. we'll then subtract each point from the corresponding
            # value in the first.
            i_line_1 = []
            i_line_2 = []
            for j, point in enumerate(lines_top[0]):
                pt_x = point[0]
                pt_y_1 = point[1] - (average_top_space_diff * 2)
                # pt_y_1 = lines_top[0][j][1] - average_top_space_diff
                pt_y_2 = pt_y_1 - (average_top_space_diff * 2)
                i_line_1.append((pt_x, pt_y_1))
                i_line_2.append((pt_x, pt_y_2))

            # insert these. Make sure the highest line is added last.
            line_positions.insert(0, i_line_1)
            line_positions.insert(0, i_line_2)

            # now do the bottom ledger lines
            bottom_first_start_y = lines_bottom[0][0][1]
            bottom_first_end_y = lines_bottom[0][-1][1]

            bottom_second_start_y = lines_bottom[1][0][1]
            bottom_second_end_y = lines_bottom[1][-1][1]

            bottom_begin_height = bottom_second_start_y - bottom_first_start_y
            bottom_end_height = bottom_second_end_y - bottom_second_end_y

            average_bottom_space_diff = int(round((bottom_begin_height + bottom_end_height) * 0.5))

            i_line_1 = []
            i_line_2 = []
            for k, point in enumerate(lines_bottom[1]):
                pt_x = point[0]
                pt_y_1 = point[1] + (average_bottom_space_diff * 2)
                pt_y_2 = pt_y_1 + (average_bottom_space_diff * 2)
                i_line_1.append((pt_x, pt_y_1))
                i_line_2.append((pt_x, pt_y_2))
            line_positions.extend([i_line_1, i_line_2])

            # average lines y_position
            avg_lines = []
            for l, line in enumerate(av_lines[i]):
                avg_lines.append(line.average_y)
            diff_up = avg_lines[1] - avg_lines[0]
            diff_lo = avg_lines[3] - avg_lines[2]
            avg_lines.insert(0, avg_lines[0] - 2 * diff_up)
            avg_lines.insert(1, avg_lines[1] - diff_up)
            avg_lines.append(avg_lines[5] + diff_lo)
            avg_lines.append(avg_lines[5] + 2 * diff_lo)  # not using the 8th line

            self.staff_results[i] = {
                'staff_no': i + 1,
                'coords': [ulx, uly, lrx, lry],
                'num_lines': len(staff),
                'line_positions': line_positions,
                'contents': [],
                'clef_shape': None,
                'clef_line': None,
                'avg_lines': avg_lines
            }
            all_line_positions.append(self.staff_results[i])

        self.staves = all_line_positions
        if self.interpolation:
            self.staves = self._interpolate_staff_locations(self.staves)
        self._staff_coords()

    def _process_staves(self):
        self.staves = self._reorder_staves_LTR_TTB(self.staves)

    def _reorder_staves_LTR_TTB(self, staves):
        # reorder staves left to right, top to bottom

        ordered_staves = []

        # Fixes: Title page with no information bug
        if staves is None:
            return None

        # group by y intersection
        for i, st in enumerate(staves):

            # initial staff
            if not ordered_staves:
                ordered_staves.append([st])
            else:
                col_placement = -1  # vertical insert
                for j, group in enumerate(ordered_staves):

                    y_intersects = False
                    row_placement = -1  # horizontal insert

                    # find if st intersects any staff in this group
                    for k, st2 in enumerate(group):
                        if self._y_intersecting_coords(st['coords'], st2['coords'][1], st2['coords'][3]):
                            y_intersects = True,
                            if st['coords'][0] > st2['coords'][0]:
                                row_placement = k + 1   # get row pos
                            print ('y_intersects', k)

                    # place in correct row
                    if y_intersects:
                        group.insert(row_placement, st)
                        break

                    # get col pos
                    elif st['coords'][1] > max(st2['coords'][1] for st2 in group):
                        col_placement = j + 1

                if not y_intersects:
                    ordered_staves.insert(col_placement, [st])

        # number staves and flatten
        numbered_staves = []
        count = 0
        for group in ordered_staves:
            for st in group:
                count += 1
                st['staff_no'] = count
                numbered_staves.append(st)

        print ([[x['staff_no'] for x in group] for group in ordered_staves])
        print ([x['staff_no'] for x in numbered_staves])

        return numbered_staves

    def _staff_coords(self):
        """
            Returns the coordinates for each one of the staves
        """
        st_coords = []
        for i, staff in enumerate(self.staff_finder):
            st_coords.append(self.staff_results[i]['coords'])

        self.staff_bounds = st_coords

    def _auto_merge(self, staff_groups):
        # automatically merge staves on the same row

        merged_staves = []  # all staves to be returned
        merge = None
        merge_margin = self.merge_distance * self.avg_staff_height

        for i, group in enumerate(staff_groups):
            row_staves = group

            j = 0
            while j < len(row_staves):

                st1 = row_staves[j]
                st2 = None if j >= len(row_staves) - 1 else row_staves[j + 1]

                # merge
                if (st2 and
                        self._y_intersecting_coords(st1['coords'], st2['coords'], 0) and
                        self._x_intersecting_coords(st1['coords'], st2['coords'], merge_margin) and
                        st1['num_lines'] == st2['num_lines'] and
                        len(st1['line_positions']) == len(st2['line_positions'])):

                    merge = self._merge_staves(st1, st2)
                    del row_staves[j:j + 2]
                    row_staves.insert(j, merge)

                # don't merge
                else:
                    j += 1

            merged_staves.append(row_staves)
            # print[[x['staff_no']for x in group] for group in merged_staves]
            row_staves = []

        return merged_staves

    def _merge_staves(self, st1, st2):
        # combine two adjascent staves into a single staff
        # assumes st1 is directly to the left of st2
        # assumes both staves have same number of lines

        # overlap results in cutting off st2

        num_lines = st1['num_lines']
        staff_no = st1['staff_no']  # this gets replaced later during flattening

        if st1['clef_line']:
            clef_line = st1['clef_line']
        else:
            clef_line = st2['clef_line']

        if st1['clef_shape']:
            clef_shape = st1['clef_shape']
        else:
            clef_shape = st2['clef_shape']

        if st1['contents']:
            contents = st1['contents']
        else:
            contents = st2['contents']

        # get new staff coordinates
        coords = [st1['coords'][0] if (st1['coords'][0] < st2['coords'][0]) else st2['coords'][0],
                  st1['coords'][1] if (st1['coords'][1] < st2['coords'][1]) else st2['coords'][1],
                  st1['coords'][2] if (st1['coords'][2] > st2['coords'][2]) else st2['coords'][2],
                  st1['coords'][3] if (st1['coords'][3] > st2['coords'][3]) else st2['coords'][3],
                  ]

        # merge line positions
        # assumes same number of lines
        line_positions = []
        for i in range(len(st1['line_positions'])):

            # crop off any overlap from st2
            nudge = 0
            while st2['line_positions'][i][nudge][0] < st1['line_positions'][i][-1][0]:
                nudge += 1

            line_positions += [st1['line_positions'][i] + st2['line_positions'][i][nudge:]]
            # print line_positions[i]

        avg_lines = []
        for i in range(len(line_positions)):
            avg_lines += [sum(x[1] for x in line_positions[i]) / len(line_positions[i])]

        st_merge = {
            'line_positions': line_positions,
            'clef_line': clef_line,
            'num_lines': num_lines,
            'clef_shape': clef_shape,
            'staff_no': staff_no,
            'coords': coords,
            'avg_lines': avg_lines,
            'contents': contents,
        }

        return st_merge

    def _flatten_and_renumber(self, grouped_staves):

        numbered_staves = []
        count = 0
        for group in grouped_staves:
            for st in group:
                count += 1
                st['staff_no'] = count
                numbered_staves.append(st)

        # print[x['staff_no'] for x in numbered_staves]
        return numbered_staves

    ###########
    # Utility
    ###########

    def _y_intersecting_coords(self, coord, ymin, ymax):
        # does rect lie within ymin and ymax
        ymin = min(ymin, ymax)
        ymax = max(ymin, ymax)

        return not (coord[1] > ymin and coord[1] > ymax or
                    coord[3] < ymin and coord[3] < ymax)

    def _flatten(self, l, ltypes=(list, tuple)):

        ltype = type(l)
        l = list(l)
        i = 0
        while i < len(l):
            while isinstance(l[i], ltypes):
                if not l[i]:
                    l.pop(i)
                    i -= 1
                    break
                else:
                    l[i:i + 1] = l[i]
            i += 1
        return ltype(l)
