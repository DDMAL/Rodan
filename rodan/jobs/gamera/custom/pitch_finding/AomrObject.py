# -*- coding: UTF-8 -*-
import json
from gamera.core import *
from gamera.toolkits import musicstaves
from AomrExceptions import *
from gamera import classify
from gamera import knn

import copy
import math
from operator import itemgetter

import logging
lg = logging.getLogger('aomr')

init_gamera()


class AomrObject(object):
    """
    Manipulates an Aomr file and stores its information
    """
    def __init__(self, filename, **kwargs):
        """
            Constructs and returns an AOMR object
        """
        self.SCALE = ['g', 'f', 'e', 'd', 'c', 'b', 'a', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
        self.filename = filename
        self.extended_processing = True

        self.lines_per_staff = kwargs['lines_per_staff']
        self.sfnd_algorithm = kwargs['staff_finder']
        self.srmv_algorithm = kwargs['staff_removal']
        self.binarization = kwargs["binarization"]

        if "glyphs" in kwargs.values():
            self.classifier_glyphs = kwargs["glyphs"]
        if "weights" in kwargs.values():
            self.classifier_weights = kwargs["weights"]

        # Sketchy: discard_size is used as a milimeter value in one place, and as no of pixels in another. Do a ctrl f search.
        self.discard_size = kwargs["discard_size"]
        self.avg_punctum = None

        # the result of the staff finder. Mostly for convenience
        self.staves = None

        self.staff_locations = None
        self.staff_coordinates = None

        # a global to keep track of the number of stafflines.
        self.num_stafflines = None
        # cache this once so we don't have to constantly load it
        # If it's a string, open the file, otherwise it's the image object
        if isinstance(self.filename, basestring):
            self.image = load_image(self.filename)
        else:
            self.image = self.filename
        self.image_resolution = self.image.resolution

        if self.image.data.pixel_type != ONEBIT:
            self.image = self.image.to_greyscale()
            bintypes = ['threshold',
                        'otsu_threshold',
                        'sauvola_threshold',
                        'niblack_threshold',
                        'gatos_threshold',
                        'abutaleb_threshold',
                        'tsai_moment_preserving_threshold',
                        'white_rohrer_threshold']
            self.image = getattr(self.image, bintypes[self.binarization])(0)
            # BUGFIX: sometimes an image loses its resolution after being binarized.
            if self.image.resolution < 1:
                self.image.resolution = self.image_resolution

        # check the amount of blackness of the image. If it's inverted,
        # the black area will vastly outweigh the white area.
        area = self.image.area().tolist()[0]
        black_area = self.image.black_area()[0]

        if area == 0:
            raise AomrError("Cannot divide by a zero area. Something is wrong.")

        if (black_area / area) > 0.7:
            # if it is greater than 70% black, we'll invert the image. This is an in-place operation.
            lg.debug("Inverting the colours.")
            self.image.invert()

        self.image_size = [self.image.ncols, self.image.nrows]

        # store the image without stafflines
        self.img_no_st = None
        self.rgb = None
        self.page_result = {
            'staves': {},
            'dimensions': self.image_size
        }

    def run(self, page_glyphs, pitch_staff_technique=0,staff_point_list=None):
        lg.debug("Running the finding code.")

        print "1. Finding staves."
        self.find_staves(staff_point_list)

        print "2. Finding staff coordinates"
        self.staff_coords()

        if pitch_staff_technique is 0:
            print "3a. Finding technique is miyao."
            self.sglyphs = self.miyao_pitch_finder(page_glyphs)
        else:
            print "3b. Finding technique is average lines."
            self.sglyphs = self.avg_lines_pitch_finder(page_glyphs)

        print "5. Constructing JSON output."
        data = {}
        for s, stave in enumerate(self.staff_coordinates):
            contents = []
            for glyph, staff, offset, strt_pos, note, octave, clef_pos, clef in self.sglyphs:
                glyph_id = glyph.get_main_id()
                glyph_type = glyph_id.split(".")[0]
                glyph_form = glyph_id.split(".")[1:]

                if staff == s + 1:
                    j_glyph = {'type': glyph_type,
                               'form': glyph_form,
                               'coord': [glyph.offset_x, glyph.offset_y, glyph.offset_x + glyph.ncols, glyph.offset_y + glyph.nrows],
                               'strt_pitch': note,
                               'octv': octave,
                               'strt_pos': strt_pos,
                               'clef_pos': clef_pos,
                               'clef': clef}
                    contents.append(j_glyph)
            data[s] = {'coord': stave, 'content': contents}

        encoded = json.dumps(data)

        print "6. Returning the data. Done running for this page."
        return encoded

    def find_staves(self, staff_point_list):
        """
        """

        def __fix_staff_point_list_list(staff_point_list, staffspace_height):
            """
            """
            # print "POLY_LIST:{0}".format(poly_list)
            for poly in staff_point_list:  # loop over polygons
                #following condition checks if there are the same amount of points on all 4 staff lines
                if len(poly[0].vertices) == len(poly[1].vertices) and \
                        len(poly[0].vertices) == len(poly[2].vertices) and \
                        len(poly[0].vertices) == len(poly[3].vertices):
                    continue
                else:
                    for j in xrange(0, len(poly)):  # loop over all 4 staff lines
                        for k in xrange(0, len(poly[j].vertices)):  # loop over points of staff
                            for l in xrange(0, len(poly)):  # loop over all 4 staff lines
                                if l == j:  # optimization to not loop through the same staff line as outer loop
                                    continue

                                if(k < len(poly[l].vertices)):  # before doing the difference make sure index k is within indexable range of poly[l]
                                    y_pix_diff = poly[j].vertices[k].x - poly[l].vertices[k].x
                                else:
                                    #if it's not in range, we are missing a point since, the insertion grows the list as we go through the points
                                    y_pix_diff = -10000  # arbitrary value to evaluate next condition to false and force an insert

                                if(y_pix_diff < 3 and y_pix_diff > -3):  # if the y coordinate pixel difference within acceptable deviation
                                    continue
                                else:
                                    #missing a point on that staff
                                    staffspace_multiplier = (l - j)  # represents the number of staff lines apart from one another
                                    poly[l].vertices.insert(k, Point(poly[j].vertices[k].x, poly[j].vertices[k].y + (staffspace_multiplier * staffspace_height)))
            return staff_point_list

        if staff_point_list is None:
            if self.sfnd_algorithm is 0:
                s = musicstaves.StaffFinder_miyao(self.image)
                self.stspace_height = s.staffspace_height
                # print self.stspace_height
            elif self.sfnd_algorithm is 1:
                s = musicstaves.StaffFinder_dalitz(self.image)
            elif self.sfnd_algorithm is 2:
                s = musicstaves.StaffFinder_projections(self.image)
            else:
                raise AomrStaffFinderNotFoundError("The staff finding algorithm was not found.")

            scanlines = 20
            blackness = 0.8
            tolerance = -1

            # there is no one right value for these things. We'll give it the old college try
            # until we find something that works.
            while not self.staves:
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
                self.staves = s.get_polygon()

                if not self.staves:
                    lg.debug("No staves found. Decreasing blackness.")
                    blackness -= 0.1

            __fix_staff_point_list_list(self.staves, self.stspace_height)

        else:
            self.staves = staff_point_list
            # the following object instansitation and value injection is to be able to compute s.get_average()
            # in order to bypass populating s.linelist with the staff_find() function inside the class
            s = musicstaves.StaffFinder_miyao(self.image)
            s.linelist = staff_point_list
            av_lines = s.get_average()

        # if len(self.staves) < self.lines_per_staff:
        #     # the number of lines found was less than expected.
        #     return None

        all_line_positions = []
        # stave_fix = self.__fix_poly_point_list(self.staves)
        # print "STAVES_FIXED:{0}".format(stave_fix)

        for i, staff in enumerate(self.staves):
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
            diff_up = avg_lines[1]-avg_lines[0]
            diff_lo = avg_lines[3]-avg_lines[2]
            avg_lines.insert(0, avg_lines[0] - 2 * diff_up)
            avg_lines.insert(1, avg_lines[1] - diff_up)
            avg_lines.append(avg_lines[5] + diff_lo)
            avg_lines.append(avg_lines[5] + 2 * diff_lo)  # not using the 8th line

            self.page_result['staves'][i] = {
                'staff_no': i+1,
                'coords': [ulx, uly, lrx, lry],
                'num_lines': len(staff),
                'line_positions': line_positions,
                'contents': [],
                'clef_shape': None,
                'clef_line': None,
                'avg_lines': avg_lines
            }
            all_line_positions.append(self.page_result['staves'][i])

        self.staff_locations = all_line_positions

        return True

    def staff_coords(self):
        """
            Returns the coordinates for each one of the staves
        """
        st_coords = []
        if self.staves is None or len(self.staves) == 0:
            raise AomrUnableToFindStavesError("No staff lines were found. Make sure you binarized the image correctly before getting to this step.")

        for i, staff in enumerate(self.staves):
            st_coords.append(self.page_result['staves'][i]['coords'])

        self.staff_coordinates = st_coords
        return st_coords

    def remove_stafflines(self):
        """ Remove Stafflines.
            Removes staves. Stores the resulting image.
        """
        if self.srmv_algorithm == 0:
            musicstaves_no_staves = musicstaves.MusicStaves_rl_roach_tatem(self.image, 0, 0)
        elif self.srmv_algorithm == 1:
            musicstaves_no_staves = musicstaves.MusicStaves_rl_fujinaga(self.image, 0, 0)
        elif self.srmv_algorithm == 2:
            musicstaves_no_staves = musicstaves.MusicStaves_linetracking(self.image, 0, 0)
        elif self.srmv_algorithm == 3:
            musicstaves_no_staves = musicstaves.MusicStaves_rl_carter(self.image, 0, 0)
        elif self.srmv_algorithm == 4:
            musicstaves_no_staves = musicstaves.MusicStaves_rl_simple(self.image, 0, 0)

        # grab the number of stafflines from the first staff. We'll use that
        # as the global value
        num_stafflines = self.page_result['staves'][0]['num_lines']
        musicstaves_no_staves.remove_staves(u'all', num_stafflines)
        self.img_no_st = musicstaves_no_staves.image

    def avg_lines_pitch_finder(self, glyphs):
        """ Pitch Find.
            pitch find algorithm for all glyphs in a page
            Returns a list of processed glyphs with the following structure:
                glyph, stave_number, offset_x, note_name, start_position
        """
        proc_glyphs = []  # processed glyphs
        av_punctum = self.average_punctum(glyphs)
        for g in glyphs:
            glyph_id = g.get_main_id()
            glyph_type = glyph_id.split(".")[0]
            if glyph_type != '_group':
                if glyph_type == 'neume':
                    center_of_mass = self.process_neume(g)
                else:
                    center_of_mass = self.x_projection_vector(g)
                glyph_array = self.glyph_staff_y_pos_ave(g, center_of_mass)
                strt_pos = 2 * (glyph_array[0][2]) + glyph_array[0][0] + 2
                stave = glyph_array[0][1] + 1
                if glyph_type == 'division' or glyph_type == 'alteration':
                    note = None
            else:
                note = None
                stave = None
                strt_pos = None

            proc_glyphs.append([g, stave, g.offset_x, strt_pos])

        sorted_glyphs = self.sort_glyphs(proc_glyphs)
        return sorted_glyphs

    def miyao_pitch_finder(self, glyphs):
        """
            Returns a set of glyphs with pitches
        """
        proc_glyphs = []
        st_bound_coords = self.staff_coordinates
        st_full_coords = self.staff_locations

        # what to do if there are no punctum on a page???
        av_punctum = self.average_punctum(glyphs)

        for g in glyphs:
            g_cc = None
            sub_glyph_center_of_mass = None
            glyph_id = g.get_main_id()
            glyph_var = glyph_id.split('.')
            glyph_type = glyph_var[0]

            if glyph_type == 'neume':
                center_of_mass = self.process_neume(g)
            else:
                center_of_mass = self.x_projection_vector(g)

            if glyph_type == '_group':
                continue
                # strt_pos = None
                # st_no = None
                # center_of_mass = 0
            else:
                stinfo = self._return_staff_no(g, center_of_mass)
                if stinfo is None:
                    continue
                else:
                    staff_locations, staff_number = stinfo

                miyao_line = self._return_vertical_line(g, staff_locations[0])

                if glyph_type == 'division' or glyph_type == 'alteration':
                    strt_pos = None
                elif glyph_type == "neume" or glyph_type == "custos" or glyph_type == "clef":
                    line_or_space, line_num = self._return_line_or_space_no(g, center_of_mass, staff_locations, miyao_line)  # line (0) or space (1), no
                    strt_pos = self.strt_pos_find(g, line_or_space, line_num)

                else:
                    strt_pos = None
                    staff_number = None

            proc_glyphs.append([g, staff_number, g.offset_x, strt_pos])

        sorted_glyphs = self.sort_glyphs(proc_glyphs)

        return sorted_glyphs

    def biggest_cc(self, g_cc):
        """
            Returns the biggest cc area glyph
        """
        sel = 0
        black_area = 0
        for i, each in enumerate(g_cc):
            if each.black_area() > black_area:
                black_area = each.black_area()
                sel = i
        return g_cc[sel]

    def strt_pos_find(self, glyph, line_or_space, line_num):
        """ Start position finding.
            Returns the start position, starting from ledger line 0, which strt_pos value is 0.
        """
        strt_pos = (line_num + 1)*2 + line_or_space
        return strt_pos

    def find_octave(self, clef, clef_line, my_strt_pos):
        clef_type = clef.split(".")[-1]  # "f" or "c"
        dividing_line = clef_line
        octv = 0
        actual_line = 10 - (2*(clef_line-1))

        if clef_type == "c":
            if my_strt_pos <= actual_line:
                octv = 4
            elif my_strt_pos > actual_line + 7:
                octv = 2
            else:
                octv = 3
        elif clef_type == "f":
            if (actual_line + 3) >= my_strt_pos > (actual_line - 3):
                octv = 3
            elif my_strt_pos < (actual_line - 3):
                octv = 4
            elif my_strt_pos > (actual_line + 3):
                octv = 2
        return octv

    def sort_glyphs(self, proc_glyphs):
        """
            Sorts the glyphs by its place in the page (up-bottom, left-right) and appends the proper note
            according to the clef at the beginning of each stave
        """
        sorted_glyphs = sorted(proc_glyphs, key=itemgetter(1, 2))

        # declare this, otherwise it might be undefined if a clef isn't the first
        # thing on the line. It's probably incorrect, but it's better than
        # exploding.
        shift = 0
        my_clef = None
        my_clef_line = None

        def __glyph_type(g):
            return g[0].get_main_id().split(".")[0]

        for i, glyph_array in enumerate(sorted_glyphs):
            gtype = __glyph_type(glyph_array)
            if gtype == 'clef':
                # my_clef = this_glyph_id

                # my_clef_line = copy.deepcopy(glyph_array[3])
                # clef shift ensures we use the real lines, not the imaginary ones.
                shift = self.clef_shift(glyph_array)
                # array 3 is the glyph_strt_pos
                glyph_array[3] = 6 - glyph_array[3] / 2
                glyph_array.extend([None, None, None, None])
            elif gtype == "neume" or gtype == "custos":
                pitch = self.SCALE[glyph_array[3] - shift]
                # find the nearest prior clef.
                revglyphs = reversed(sorted_glyphs[0:i])
                for gl in revglyphs:
                    if __glyph_type(gl) == "clef":
                        my_clef = gl[0].get_main_id()
                        my_clef_line = copy.deepcopy(gl[3])
                        break

                if my_clef is None:
                    print "My clef is None! setting default c clef for {0}".format(glyph_array)
                    my_clef = "clef.c"
                if my_clef_line is None:
                    print "My clef_line is None! setting default of line 3 for {0}".format(glyph_array)
                    my_clef_line = 3

                octave = self.find_octave(my_clef, my_clef_line, glyph_array[3])
                glyph_array.extend([pitch, octave, my_clef_line, my_clef])
            else:
                # pdb.set_trace()
                glyph_array.extend([None, None, None, None])

        return sorted_glyphs

    def clef_shift(self, glyph_array):
        """ Clef Shift.
            This methods shifts the note names depending on the staff clef
        """
        this_clef = glyph_array[0]
        this_clef_id = this_clef.get_main_id()
        try:
            this_clef_type = this_clef_id.split(".")[1]
        except IndexError:
            # in case we've got an error.
            this_clef_type = "c"

        shift = 0
        if this_clef_type == 'c':
            shift = glyph_array[3] - 4
            return shift
        elif this_clef_type == 'f':
            shift = glyph_array[3] - 1
            return shift

    def _return_staff_no(self, g, center_of_mass):
        """
            Returns the staff and staff number where a specific glyph is located
        """
        for i, s in enumerate(self.staff_coordinates):
            staff_number = i + 1
            if 0.5 * (3 * s[1] - s[3]) <= g.offset_y + center_of_mass < 0.5 * (3 * s[3] - s[1]):
                staff_location = self.staff_locations[i]['line_positions']
                return staff_location, staff_number

    def _return_vertical_line(self, g, st):
        """
            Returns the miyao line number just after the glyph, starting from 0
        """

        # TODO: FIXME. I always return 0.
        for j, stf in enumerate(st[1:]):
            if int(stf[0]) > int(g.offset_x):
                return j
        else:
            return j

    def _return_line_or_space_no(self, glyph, center_of_mass, st, miyao_line):
        """
            Returns the line or space number where the glyph is located for a specific stave an miyao line.

            Remember kids :)
                Line = 0
                Space = 1
        """

        horz_diff = float(st[0][miyao_line][0] - st[0][miyao_line-1][0])

        for i, stf in enumerate(st[1:]):
            vert_diff_up = float(stf[miyao_line][1] - stf[miyao_line-1][1])  # y_pos difference with the upper miyao line
            vert_diff_lo = float(stf[miyao_line+1][1] - stf[miyao_line][1])  # y_pos difference with the lower miyao line
            factor_up = vert_diff_up / horz_diff
            factor_lo = vert_diff_lo / horz_diff
            diff_x_glyph_bar = float(glyph.offset_x - stf[miyao_line-1][0])  # difference between the glyph x_pos and the previous bar
            vert_pos_shift_up = factor_up * diff_x_glyph_bar  # vert_pos_shift is the shifted vertical position of each line for each x position
            vert_pos_shift_lo = factor_lo * diff_x_glyph_bar  # vert_pos_shift is the shifted vertical position of each line for each x position
            diff = (stf[miyao_line][1] + vert_pos_shift_lo) - (st[i][miyao_line-1][1] + vert_pos_shift_up)
            if stf[miyao_line][1] + 6 * diff / 16 > glyph.offset_y + center_of_mass:
                line_or_space = 0
                return line_or_space, i

            elif stf[miyao_line][1] + 13 * diff / 16 > glyph.offset_y + center_of_mass:
                line_or_space = 1
                return line_or_space, i

            elif stf[miyao_line][1] + 4 * diff / 4 > glyph.offset_y + center_of_mass:
                line_or_space = 0
                return line_or_space, i+1

    def glyph_classification(self):
        """ Glyph classification.
            Returns a list of the classified glyphs with its position and size.
        """
        cknn = knn.kNNInteractive([],
                                ["area",
                                "aspect_ratio",
                                "black_area",
                                "compactness",
                                "moments",
                                "ncols_feature",
                                "nholes",
                                "nholes_extended",
                                "nrows_feature",
                                "skeleton_features",
                                "top_bottom",
                                "volume",
                                "volume16regions",
                                "volume64regions",
                                "zernike_moments"],
                                True,
                                8)

        cknn.from_xml_filename(self.classifier_glyphs)
        cknn.load_settings(self.classifier_weights)  # Option for loading the features and weights of the training stage.

        ccs = self.img_no_st.cc_analysis()
        grouping_function = classify.ShapedGroupingFunction(16)  # variable ?
        self.classified_image = cknn.group_and_update_list_automatic(ccs, grouping_function, max_parts_per_group=4)  # variable ?

    def pitch_finding(self):
        """ Pitch finding.
            Returns a list of pitches for a list of classified glyphs.
        """
        # this filters glyphs under a certain size. Remember we're working
        # in tenths of a mm and not aboslute pixels
        def __check_size(c):
            return self._m10(c.width) > self.discard_size or self._m10(c.height) > self.discard_size
        cls_img = [c for c in self.classified_image if __check_size(c)]
        self.classified_image = cls_img

        glyph_list = {}
        for i, c in enumerate(self.classified_image):
            snum = self._get_staff_by_coordinates(c.center_x, c.center_y)

            if snum is not None:
                if snum not in glyph_list.keys():
                    glyph_list[snum] = []
                glyph_list[snum].append([c.ul_x, c.ul_y, c])

        for staff, glyphs in glyph_list.iteritems():
            glyphs.sort()
            for g, glyph in enumerate(glyphs):
                self.rgb.draw_text((glyph[2].ll_x, glyph[2].ll_y), "X-{0}".format(g), RGBPixel(255, 0, 0), 12, 0, False, False, 0)
                o = glyph.splitx(0.2)  # should be in 10mm instead of percentage

    # private
    def _m10(self, pixels):
        """
            Converts the number of pixels to the number of 10ths of a MM.
            This allows us to be fairly precise while still using whole numbers.
            mm10 (micrometre) was chosen as it is a common metric typographic unit.
            Returns an integer of the number of mm10.
        """
        # 25.4 mm in an inch * 10.
        return int(round((pixels * 254) / self.image.resolution))

    def _get_staff_by_coordinates(self, x, y):
        for k, v in self.page_result['staves'].iteritems():
            top_coord = v['line_positions'][0][0]
            bot_coord = v['line_positions'][-1][-1]

            # y is the most important for finding which staff it's on
            if top_coord[1] <= y <= bot_coord[1]:
                # add 20 mm10 to the x values, since musicstaves doesn't
                # seem to accurately guess the starts and ends of staves.
                if top_coord[0] - self._m10(20) <= x <= bot_coord[0] + self._m10(20):
                    return k
        return None

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

    def average_punctum(self, glyphs):
        """ Average Punctum.
            returns the average number of columns of the punctums in a given page
        """
        wide = 0
        i = 0
        avg_punctum_col = 0
        for glyph in glyphs:

            if glyph.get_main_id() == 'neume.punctum':
                wide = wide + glyph.ncols
                i = i + 1
        avg_punctum_col = wide / i

        self.avg_punctum = avg_punctum_col

    def x_projection_vector(self, glyph):
        """ Projection Vector
            creates a subimage of the original glyph and returns its center of mass
        """
        center_of_mass = 0

        if glyph.ncols > self.discard_size and glyph.nrows > self.discard_size:

            if glyph.ncols < self.avg_punctum:
                this_punctum_size = glyph.ncols
            else:
                this_punctum_size = self.avg_punctum

            temp_glyph = glyph.subimage((glyph.offset_x + 0.0 * this_punctum_size, glyph.offset_y),
                                        ((glyph.offset_x + 1.0 * this_punctum_size - 1), (glyph.offset_y + glyph.nrows - 1)))
            projection_vector = temp_glyph.projection_rows()
            center_of_mass = self.center_of_mass(projection_vector)
        else:
            center_of_mass = 0

        return center_of_mass

    def center_of_mass(self, projection_vector):
        """ Center of Mass.
            returns the center of mass of a given glyph
        """
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

    def glyph_staff_y_pos_ave(self, g, center_of_mass):
        """ Glyph Staff Average y-Position.
            calculates between what stave lines a certain glyph is located
        """
        glyph_array = []
        y = round(g.offset_y + center_of_mass)  # y is the y_position of the center of mass of a glyph
        for s, staff in enumerate(self.staff_locations):
            for l, line in enumerate(staff['avg_lines'][1:]):
                diff = (0.5 * (line - staff['avg_lines'][l]))
                if math.floor(line-diff / 2) <= y <= math.ceil(line + diff / 2):  # Is the glyph on a line ?
                    glyph_array.append([0, s, l])
                    return glyph_array
                elif math.floor(line+diff / 2) <= y <= math.ceil(line + 3 * diff / 2):  # Is the glyph on a space ?
                    glyph_array.append([1, s, l])
                    return glyph_array
                else:
                    pass
        return glyph_array

    def process_neume(self, g):
        """
            Handles the cases of glyphs as podatus, epiphonus, cephalicus, and he, ve or dot.
        """
        g_cc = None
        sub_glyph_center_of_mass = None
        glyph_id = g.get_main_id()
        glyph_var = glyph_id.split('.')
        glyph_type = glyph_var[0]
        check_additions = False

        if not self.extended_processing:
            return self.x_projection_vector(g)
        else:
            # if check_gcc has elements, we know it's got one of these in it.
            if "he" in glyph_var or "ve" in glyph_var or "dot" in glyph_var:
                check_additions = True

            # if we want to use the biggest cc (when there are dots or other things),
            # set this_glyph to the biggest_cc. Otherwise, set it to the whole glyph.
            if check_additions:
                this_glyph = self.biggest_cc(g.cc_analysis())
            else:
                this_glyph = g

            sub_glyph_center_of_mass, offset_y = self.check_special_neumes(this_glyph)

            if "podatus" in glyph_var or "epiphonus" in glyph_var or "cephalicus" in glyph_var or "scandicus" in glyph_var:
                if check_additions is True:
                    center_of_mass = this_glyph.offset_y - g.offset_y + sub_glyph_center_of_mass
                    return center_of_mass
                else:
                    center_of_mass = offset_y - this_glyph.offset_y + sub_glyph_center_of_mass
                    return center_of_mass

            if check_additions:
                center_of_mass = this_glyph.offset_y - g.offset_y + self.x_projection_vector(this_glyph)
                return center_of_mass

            # if we've made it this far then we just return the plain old projection vector.
            return self.x_projection_vector(g)

    def check_special_neumes(self, glyph):
        glyph_var = glyph.get_main_id().split('.')

        if "podatus" in glyph_var or "epiphonus" in glyph_var:
            this_glyph = glyph.splity()[1]
        elif "cephalicus" in glyph_var or "scandicus" in glyph_var:
            this_glyph = self.biggest_cc(glyph.splity())
        else:
            this_glyph = glyph
        sub_glyph_center_of_mass = self.x_projection_vector(this_glyph)
        return sub_glyph_center_of_mass, this_glyph.offset_y
