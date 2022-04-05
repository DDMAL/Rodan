from gamera import gamera_xml
from gamera.plugins.image_utilities import union_images
from operator import itemgetter, attrgetter


class PitchFinder(object):

    def __init__(self, **kwargs):

        self.discard_size = kwargs['discard_size']

        self.SCALE = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        self.clef = 'c', 7              # default clef

        self.transpose = 0              # shift all notes by x 2nds
        self.space_proportion = 0.5     # space when within middle portion between lines
        self.get_staff_margin = 2.0     # glyphs are on staff when within x punctums above/below it
        self.always_find_staff_no = False

        self.avg_punctum = None

        self.staffless_glyphs = ['skip']        # any staffless glyph IS pitchless
        self.pitchless_glyphs = ['division']

        self.glyphs = None
        self.staves = None

        self.sorted_glyphs = None

    ##########
    # Public
    ##########

    def get_pitches(self, glyphs, staves):

        self._parse_inputs(glyphs, staves)
        self._find_pitches(self.glyphs)

        pitch_feature_names = ['staff', 'offset', 'strt_pos', 'note', 'octave', 'clef_pos', 'clef']

        output = []
        for i, g in enumerate(self.sorted_glyphs):

            cur_json = {}
            pitch_info = {}
            glyph_info = {}

            # get pitch information
            for j, pf in enumerate(g[1:]):
                pitch_info[pitch_feature_names[j]] = str(pf)
            cur_json['pitch'] = pitch_info

            # print g[0].get_main_id()

            # get glyph information
            glyph_info['bounding_box'] = {
                'ncols': g[0].ncols,
                'nrows': g[0].nrows,
                'ulx': g[0].ul.x,
                'uly': g[0].ul.y,
            }
            glyph_info['state'] = gamera_xml.classification_state_to_name(g[0].classification_state)
            glyph_info['name'] = g[0].id_name[0][1]
            cur_json['glyph'] = glyph_info

            output.append(cur_json)

        return output

    ########
    # Main
    ########

    def _parse_inputs(self, glyphs, staves):
        # filter out skips
        self.glyphs = list(filter(lambda g: g.get_main_id() != 'skip', glyphs))
        self.staves = staves

        self.avg_punctum = self._average_punctum(self.glyphs)

    def _find_pitches(self, glyphs):
        # Returns a set of glyphs with pitches

        proc_glyphs = []

        for g in self.glyphs:
            glyph_var = g.get_main_id().split('.')
            glyph_type = glyph_var[0]

            center_of_mass = self._x_projection_vector(g)

            # find staff for current glyph
            stinfo = self._get_staff_no(g, center_of_mass)
            if not stinfo:
                strt_pos, staff_number = None, None
            else:
                staff_locations, staff_number = stinfo

                if glyph_type not in self.pitchless_glyphs:
                    line_or_space, line_num = self._return_line_or_space_no(g, center_of_mass, staff_locations)
                    strt_pos = self._strt_pos_find(line_or_space, line_num)
                    # print staff_number, glyph_var, line_or_space, line_num
                else:
                    strt_pos = None
                    staff_number = None

                proc_glyphs.append([g, staff_number, g.offset_x, strt_pos])

        self.sorted_glyphs = self._sort_glyphs(proc_glyphs)

        # print self.staff_finder
        # print self.staves
        # print self.interpolated_staves
        # print '\n\n', self.staff_bounds

    ##################
    # Glyph Position
    ##################

    def _x_projection_vector(self, glyph):
        # creates a subimage of the original glyph
        # and returns its center of mass

        g = glyph
        y_add = 0

        if 'clef.f' in glyph.get_main_id():
            g, y_add = self._vector_process_f_clef(g)

        center_of_mass = 0

        if g.ncols > self.discard_size and g.nrows > self.discard_size:
            if g.ncols < self.avg_punctum:
                this_punctum_size = g.ncols
            else:
                this_punctum_size = self.avg_punctum

            temp_glyph = g.subimage((g.offset_x + 0.0 * this_punctum_size, g.offset_y),
                                    ((g.offset_x + 1.0 * this_punctum_size - 1), (g.offset_y + g.nrows - 1)))
            projection_vector = temp_glyph.projection_rows()
            center_of_mass = self._center_of_mass(projection_vector)

        else:
            center_of_mass = 0

        return center_of_mass + y_add

    def _center_of_mass(self, projection_vector):
        com = 0.
        s = 0.
        v = 0.
        for i, value in enumerate(projection_vector):
            s = s + (i + 1) * value
            v = v + value
        if v == 0:
            return com
        com = s / v
        return com

    def _vector_process_f_clef(self, glyph):
        # use only right portion of f clefs when getting center_of_mass
        g = None

        for gl in glyph.splitx(0.5):
            gl_coords = self._convert_bb_to_coords(self._get_glyph_bb(gl))

            # no g
            if not g:
                g = gl

            # left of g
            elif gl.offset_x + gl.ncols < g.offset_x:
                pass

            # x-intersecting g
            elif self._x_intersecting_coords(gl_coords, g.offset_x, g.offset_x + g.ncols, 0):
                g = union_images([g, gl])

            # right of g
            elif gl.offset_x >= g.offset_x + g.ncols:
                g = gl

        y_add = g.offset_y - glyph.offset_y

        return g, y_add

    #################
    # Closest Staff
    #################

    def _get_staff_no(self, g, center_of_mass):
        # find which staff a glyph belongs to
        if g.get_main_id().split('.')[0] in self.staffless_glyphs:
            return None

        glyph_coords = [g.offset_x, g.offset_y, g.offset_x + g.ncols, g.offset_y + g.nrows]

        max_intersection = 0
        intersecting_staff = None

        y_bound_staves = []

        for i, st in enumerate(self.staves):
            staff_coords = self._convert_bb_to_coords(st['bounding_box'])

            # intersecting staves
            amount = self._coord_intersect_area(glyph_coords, staff_coords)
            if amount > max_intersection:
                max_intersection = amount
                intersecting_staff = st
                # print 'found intersecting staff', st['staff_no']

            # y bounded staves
            if self._y_intersecting_coords(glyph_coords, staff_coords[1], staff_coords[3], int(self.get_staff_margin * self.avg_punctum)):
                y_bound_staves.append(st)
                # print 'Y BOUND', st['staff_no']

        # 1. Glyph is on a staff it intersects
        if intersecting_staff:
            return intersecting_staff['line_positions'], intersecting_staff['staff_no']

        # 2. Glyph is on closest staff whose y range contains it
        elif y_bound_staves:
            return self._find_closest_y_staff_no(g, center_of_mass, y_bound_staves)

        # 3. Glyph is on closest staff (shortest line to edge)
        elif self.always_find_staff_no:
            return self._find_closest_staff_no(g, center_of_mass, self.staves)

        # Glyph has no staff
        else:
            return None

    def _coord_intersect_area(self, coord1, coord2):
        # returns the intersection area of two rectangles
        l = max(coord1[0], coord2[0])
        b = max(coord1[1], coord2[1])
        r = min(coord1[2], coord2[2])
        t = min(coord1[3], coord2[3])

        if not (l < r and b < t):
            return 0
        else:
            return (r - l) * (t - b)

    def _find_closest_y_staff_no(self, g, center_of_mass, staves):
        com_point = (g.offset_x + g.ncols, g.offset_y + center_of_mass)

        closest = None
        for i, st in enumerate(staves):
            coord = self._convert_bb_to_coords(st['bounding_box'])
            distances = [abs(com_point[0] - coord[0]),
                         abs(com_point[0] - coord[2])]

            if closest == None or closest[0] > min(distances):
                closest = (min(distances), st['line_positions'], st['staff_no'])

        return closest[1:]

    def _find_closest_staff_no(self, g, center_of_mass, staves):
        com_point = (g.offset_x, g.offset_y + center_of_mass)

        closest = None
        for i, st in enumerate(staves):
            coord = self._convert_bb_to_coords(st['bounding_box'])

            # print i, '/', len(staves) - 1

            # define corner points
            ul = (coord[0], coord[1])
            ur = (coord[2], coord[1])
            ll = (coord[0], coord[3])
            lr = (coord[2], coord[3])

            d1 = self._find_distance_between_line_and_point(ul, ur, com_point)
            d2 = self._find_distance_between_line_and_point(ur, lr, com_point)
            d3 = self._find_distance_between_line_and_point(lr, ll, com_point)
            d4 = self._find_distance_between_line_and_point(ll, ul, com_point)
            distances = [d1, d2, d3, d4]

            if closest == None or closest[0] > min(distances):
                closest = (min(distances), st['line_positions'], st['staff_no'])
                # print closest[0], i

        return closest[1:]

    def _find_distance_between_line_and_point(self, p1, p2, p3):
        # finds minimum distance between a point and a line segment
        # line MUST be either perfectly vertical or perfectly horizontal

        x1, y1 = p1  # line start
        x2, y2 = p2  # line end
        x3, y3 = p3  # comparison point

        line_type = ('vertical' if x1 == x2 else 'horizontal')

        if line_type is 'vertical':
            perp = y3 < max([y1, y2]) and y3 > min([y1, y2])
        elif line_type is 'horizontal':
            perp = x3 < max([x1, x2]) and x3 > min([x1, x2])

        # print(perp, line_type, p1, p2, p3)
        if not perp:
            s1 = self._find_distance_between_points(p3, p1)
            s2 = self._find_distance_between_points(p3, p2)
            return min([s1, s2])
        elif line_type is 'vertical':
            return abs(float(x3 - x1))
        elif line_type is 'horizontal':
            return abs(float(y3 - y1))

    def _find_distance_between_points(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5

    ######################
    # Get Pitch Position
    ######################

    def _return_line_or_space_no(self, glyph, center_of_mass, staff):
        """
            Returns the line or space number where the glyph is located for a specific stave an miyao line.

            Remember kids :)
            0 = space
            1 = line

            0   0   1            ---------                     ledger 2
            1       2
            0   1   3            ---------                     ledger 1
            1       4
            0   2   5   --------------------------------       line 4
            1       6
            0   3   7   --------------------------------       line 3
            1       8
            0   4   9   --------------------------------       line 2
            1       10
            0   5   11  --------------------------------       line 1
            1       12
            0   6   13           ---------                     ledger -1
            1       14
            0   7   15           ---------                     ledger -2
            ......

        """
        # center_of_mass point to compare with staff lines
        ref_x = glyph.offset_x
        ref_y = int(glyph.offset_y + center_of_mass)
        line_pos = None

        # clefs snap to lines only
        line_snap = True if 'clef' in glyph.get_main_id().split('.')[0] else False

        # find left/right staffline position to compare against center_of_mass
        for i, point in enumerate(staff[0]):
            if point[0] > ref_x:
                if i == 0:
                    line_pos = [i]          # if before staff, use first line point
                else:
                    line_pos = [i - 1, i]   # if inside, use surrounding line points
                break
            elif i == len(staff[0]) - 1:
                line_pos = [i]              # if after staff, use last line point

        # print line_pos, (ref_x, ref_y)

        # find line below center_of_mass
        for i, line in enumerate(staff[1:]):
            last_line = staff[i]

            # get points left & right of center_of_mass on this line and above
            pa_left = last_line[line_pos[0]]
            pb_left = line[line_pos[0]]
            pa_right = last_line[line_pos[1]] if len(line_pos) == 2 else None
            pb_right = line[line_pos[1]] if len(line_pos) == 2 else None

            # get line functions below and above glyph
            func_above = self._gen_line_func(pa_left, pa_right)
            func_below = self._gen_line_func(pb_left, pb_right)

            # find y for each line
            y_above = func_above(ref_x)
            y_below = func_below(ref_x)

            # print pa_left, pa_right, '\t:\t', pb_left, pb_right
            # print y_above, '\t\t\t:\t', y_below

            if line_snap and y_below >= ref_y:
                y_dif = y_below - y_above
                y_mid = y_above + y_dif / 2

                if ref_y < y_mid:
                    return 0, i
                elif ref_y >= y_mid:
                    return 0, i + 1

            elif y_below >= ref_y:
                y_dif = y_below - y_above
                y_mid = y_above + y_dif / 2

                space = y_mid - (y_dif * self.space_proportion / 2), \
                    y_mid + (y_dif * self.space_proportion / 2)

                # print '\n', ref_x, ref_y, line_pos, '\n'

                # print int(y_above), int(min(space)), int(max(space)), int(y_below)

                # upper line
                if ref_y < min(space):
                    # print 'line', i
                    return 0, i

                # within space
                elif ref_y >= min(space) and ref_y <= max(space):
                    # print 'space', i
                    return 1, i

                # lower line
                elif ref_y > max(space):
                    # print 'line', i + 1
                    return 0, i + 1

                else:
                    'this is impossible'

        # glyph is below staff
        return 0, len(staff)

    def _gen_line_func(self, point_left, point_right):
        # generates a line function based on two points,
        # func(x) = y
        if point_right != None:
            m = float(point_right[1] - point_left[1]) / float(point_right[0] - point_left[0])
            b = point_left[1] - (m * point_left[0])
            return lambda x: (m * x) + b

        else:   # flat line
            return lambda x: point_left[1]

    #################
    # Pitch Finding
    #################

    def _strt_pos_find(self, line_or_space, line_num):
        # sets 0 as the 2nd ledger line above a staff
        return (line_num + 1) * 2 + line_or_space - 1 - self.transpose

    def _sort_glyphs(self, proc_glyphs):

        def __glyph_type(g):
            return g[0].get_main_id().split(".")[0]

        # Sorts the glyphs by its place in the page (up-bottom, left-right) and appends
        # the proper note according to the clef at the beginning of each stave
        sorted_glyphs = sorted(proc_glyphs, key=itemgetter(1, 2))

        for i, glyph_array in enumerate(sorted_glyphs):

            gtype = __glyph_type(glyph_array)
            if gtype == 'clef':

                # overwrite last defined clef
                self.clef = glyph_array[0].get_main_id().split('.')[1], glyph_array[3]
                glyph_array[3] = 6 - glyph_array[3] / 2  # get clef line excluding spaces
                glyph_array.extend([None, None, None, None])

            elif gtype == "neume" or gtype == "custos":
                clef, clef_line = self.clef
                my_strt_pos = glyph_array[3]

                # get clef shifts
                SCALE = self.SCALE
                noteShift = (0 if SCALE.index(clef) == 0 else len(SCALE) - SCALE.index(clef) - 1)

                # find note
                note = SCALE[int((clef_line - my_strt_pos + noteShift) % len(SCALE))]

                # find octave
                if my_strt_pos <= clef_line:
                    octave = 3 + int((clef_line - my_strt_pos + noteShift) / len(SCALE))
                elif my_strt_pos > clef_line:
                    octave = 3 - int((len(SCALE) - clef_line + my_strt_pos - 1 - noteShift) / len(SCALE))

                glyph_array.extend([note, octave, clef_line, 'clef.' + clef])
                # print clef, note, octave, glyph_array[1:], glyph_array[0].get_main_id()

            else:   # no pitch info necessary
                glyph_array.extend([None, None, None, None])

        return sorted_glyphs

    ###########
    # Utility
    ###########

    def _average_punctum(self, glyphs):
        width_sum = 0
        num_punctums = 0
        for g in glyphs:
            if g.get_main_id() == 'neume.punctum':
                width_sum += g.ncols
                num_punctums += 1

        if num_punctums > 0:
            return width_sum / num_punctums
        else:
            return 0  # no average punctums, so no average size

    def _get_glyph_bb(self, glyph):
        bb = {
            'ulx': glyph.offset_x,
            'uly': glyph.offset_y,
            'ncols': glyph.ncols,
            'nrows': glyph.nrows,
        }

        return bb

    def _convert_bb_to_coords(self, bounding_box):
        # bounding box -> coordinates
        ulx = bounding_box['ulx']
        uly = bounding_box['uly']
        lrx = ulx + bounding_box['ncols']
        lry = uly + bounding_box['nrows']

        return [ulx, uly, lrx, lry]

    def _x_intersecting_coords(self, coord, xstart, xend, margin):
        xmin = min(xstart, xend)
        xmax = max(xstart, xend)

        return not (coord[0] > xmin - margin and coord[0] > xmax + margin or
                    coord[2] < xmin - margin and coord[2] < xmax + margin)

    def _y_intersecting_coords(self, coord, ystart, yend, margin):
        # does rect lie within ystart and yend
        ymin = min(ystart, yend)
        ymax = max(ystart, yend)

        return not (coord[1] > ymin - margin and coord[1] > ymax + margin or
                    coord[3] < ymin - margin and coord[3] < ymax + margin)
