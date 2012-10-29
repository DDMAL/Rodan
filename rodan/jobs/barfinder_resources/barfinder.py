from gamera.core import *
from gamera.toolkits import musicstaves, lyric_extraction, border_removal
from gamera.classify import BoundingBoxGroupingFunction, ShapedGroupingFunction
from gamera import classify
from gamera import knn
import PIL, os
import argparse

from meicreate import BarlineDataConverter
from pymei import MeiElement
import re
from pyparsing import nestedExpr
import sys
import collections
import sets

class BarlineFinder:

    def _staffline_removal(self, image):
        """
        """
        i = musicstaves.MusicStaves_rl_roach_tatem(image, 0, 0)
        i.remove_staves(u'all', 5)
        return i.image

    def _despeckle(self, image):
        """
        """
        return image.despeckle(100)

    def _most_frequent_run_filter(self, image, mfr):
        """
        """
        filtered_image = image.image_copy()
        filtered_image.filter_short_runs(mfr + 2, 'black') # most frequent run plus 1 pixel
        filtered_image.despeckle(100)
        return filtered_image

    def _ccs(self, proc_image):
        """
        Performs connected component analysis and filters 
        using a certain set of features.
        """
        ccs = proc_image.cc_analysis()
        ccs_bars = []
        for c in ccs:
                if c.aspect_ratio()[0] <= 0.20 and c.ncols <= 15: # try other features and/or values
                    ccs_bars.append(c)
        # lg.debug(ccs_bars)
        return ccs_bars

    def _staff_line_position(self, image):
        """Finds the staff line position, but also corrects the output
        of the Miyao staff finder algorithm by connecting candidate
        sub-staves according to their position in the score, trying
        to glue related staves.

        Returns a vector with the vertices for each staff with the form 
        [(staff_number, x1, y1, x2, y2)], starting from number 1
        """

        stf_instance = musicstaves.StaffFinder_miyao(image, 0, 0)
        stf_instance.find_staves(5, 20, 0.8, -1) # 5 lines
        polygon = stf_instance.get_polygon()
        sc_position = [] # staff candidate
        stf_position = []


        for i, p in enumerate(polygon):
            ul = p[0].vertices[0]
            ur = p[0].vertices[-1]
            ll = p[len(p)-1].vertices[0]
            lr = p[len(p)-1].vertices[-1]

            x1 = ul.x
            y1 = ul.y
            x2 = lr.x
            y2 = lr.y
            sc_position.append([i + 1, x1, y1, x2, y2])

        # Glueing the output of the Miyao staff finder
        stf_position.append((sc_position[0]))
        j = 1
        for k, sc in enumerate(sc_position[1:]):
            x1 = stf_position[-1][1]
            y1 = stf_position[-1][2]
            x2 = stf_position[-1][3]
            y2 = stf_position[-1][4]
            mid_y = (sc[2]+sc[4])/2

            # Checks if a staff candidate lies in the same y-range that the previous one
            if y2 > mid_y > y1:
                # If the bounding box of the staff candidate upper left x-value is larger than 
                # the previous bounding box, and also if this value is larger than the previous 
                # difference:
                if sc[1] >= x1 and sc[1] - x1 >= x2 - x1:
                    stf_position.pop()
                    stf_position.append([j, x1, y1, sc[3], sc[4]])

                elif sc[1] < x1:
                    stf_position.pop()
                    stf_position.append([j, sc[1], sc[2], x2, y2])
            else:
                j += 1
                stf_position.append([j, sc[1], sc[2], sc[3], sc[4]])
        return stf_position

    def _system_position_parser(self, stf_position):
        """
        Returns the position of the systems
        """
        system_bb = [] # system_staff_position
        system_bb.append(stf_position[0])
        for sp in stf_position[1:]:
            if sp[5] == system_bb[-1][5]:
                if sp[1] < system_bb[-1][1]:
                    system_bb[-1][1] = sp[1]
                if sp[2] < system_bb[-1][2]:
                    system_bb[-1][2] = sp[2]
                if sp[3] > system_bb[-1][3]:
                    system_bb[-1][3] = sp[3]
                if sp[4] > system_bb[-1][4]:
                    system_bb[-1][4] = sp[4]
            else:
                system_bb.append(sp)
        return system_bb

    def _bar_candidate_check(self, bar_candidates, stf_position, system):
        """
        Several methods to discard and/or validate bar candidates:

        1) Checks if the candidate bars lie within the upper and lower 
        boundaries of each staff. 

        2) Checks if bar candidate upper o lower position lies within a stf_position

        3) Creates a barline at the beginning of each staff according 
        to the staff position by the Miyao staff finder.

        Returns a vector in the form: [[gameracore.Image, staff_no]]
        """
        # TASKS
        # 1. Glue together broken candidate bars
        # 2. Filter candidates at the L & R of staves
        # 3. Filter stems 
        # 4. Output MEI file should provide bars for all 'crossed' staves

        # PROCEDURE
        # 1. OK Calculate the system_bb for all systems
        # 2. OK Discard bar_candidates outside of all system_bb
        # 3. Discard bar_candidates with no broken parts above or below within its system_bb
        # 4. Group bar_candidates, broken or not, belonging to the same system_bb
        # 5. Assign stave number to the glued bar candidates

        # print "\nSP: {0}\n".format(stf_position) 
        checked_bars = []
        stf_height = sum([i[4]-i[2] for i in stf_position])/len(stf_position)

        # retrieves the position of the systems
        system_bb = self._system_position_parser(stf_position)    
        # print "SYSTEM_BB: {0}\n".format(system_bb)
        no_sys =  len(system_bb) # number of systems

        def __within_bb_check(bc, bb):
            """
            Checks if a bar_candidate is inside a bounding_box (system or staff)
            """
            bc_mid_x = bc.offset_x + int((bc.ncols - 1) / 2)
            bc_mid_y = bc.offset_y + int((bc.nrows - 1) / 2)
            bb_x1, bb_x2 = bb[1], bb[3]
            bb_y1, bb_y2 = bb[2], bb[4]
            if bc_mid_x > bb_x1 and bc_mid_x < bb_x2 and bc_mid_y > bb_y1 and bc_mid_y < bb_y2:
                return bb

        def __bar_candidate_grouping(ungrouped_bars):
            """
            Groups bar candidates
            """
            for bar in ungrouped_bars:
                bar.classify_heuristic('_group._part.bc')
            cknn = knn.kNNInteractive()
            cknn.set_glyphs(ungrouped_bars)
            grouped_bars = cknn.group_and_update_list_automatic(ungrouped_bars, \
                        max_parts_per_group = 10, \
                        grouping_function = BoundingBoxGroupingFunction(5000)) # Threshold distance in pixels between bounding boxes 
            return grouped_bars

        # 2. Discard bar_candidates outside of all system_bb
        filt_bar_candidates = []
        for bc in bar_candidates:
            for s in system_bb:
                bb = __within_bb_check(bc, s)
                if bb:
                    filt_bar_candidates.append([bc, bb[5]])
                    
                    break

        # 3. Discard bar_candidates with no broken parts above or below within its system_bb
        # Procedure: 
        #           for each bc, look for all bc within the same system
        #           if its height is less than stf_height (*0.75)
        #                     it should have another broken part above or below, 
        #                     otherwise it is a false positive
        sys_bars = []

        for i in xrange(no_sys):
            sys_bars.append([x for x in filt_bar_candidates if x[1] == i+1])

        for sys_bar_idx, sys_bar in enumerate(sys_bars):
            bars = []
            system_height = system_bb[sys_bar_idx][4]-system_bb[sys_bar_idx][2]

            factor = 5 # vertical tolerance for finding vertical candidates
            brok_cand_list = []
            for s_ind, s in enumerate(sys_bar): #each bar candidate within the same system

                brok_cand = [x[0] for x in sys_bar if \
                        (s[0].offset_x > (x[0].offset_x - factor * x[0].ncols) and \
                         s[0].offset_x < (x[0].offset_x + factor * x[0].ncols))]

                if not brok_cand in brok_cand_list: # if it is not already in the list of broken bar candidates
                    brok_cand_list.append(brok_cand)
                    if len(brok_cand) > 1:   

                        grouped_bars = __bar_candidate_grouping(brok_cand)
                        while len(grouped_bars) > 1:
                            # print 'GROUPING: {0}'.format(grouped_bars)
                            grouped_bars = __bar_candidate_grouping(grouped_bars) # until all candidates have been glued
                        # print 'CL_IM: {0}'.format(grouped_bars)
                        bars.append(grouped_bars[0])
 
                    elif len(brok_cand) == 1 and brok_cand[0].nrows < (system_height):
                        continue

                    else:
                        bars.append(s[0])

            # print '\nSystem {1} has {2} bars: {0}\n'.format(bars, sys_bar_idx + 1, len(bars))
            for bc in bars:
                checked_bars.append((bc, sys_bar_idx+1))
        return checked_bars 

    def _staff_number_assign(self, bars_bb, staff_bb):
        """
        Assigns staff number to all bars
        """

        def __within_bb_check(bar_bb, staff_bb):
            """
            Checks if a bar_candidate is inside a bounding_box (system or staff)
            """
            x_bar_range = (bar_bb[1], bar_bb[3])
            y_bar_range = (bar_bb[2], bar_bb[4])

            x_staff_range = (staff_bb[1], staff_bb[3])
            y_staff_range = (staff_bb[2], staff_bb[4])

            for y in xrange(y_bar_range[0], y_bar_range[1]+1):
                if y_staff_range[0] < y < y_staff_range[1]:
                    return True

        numbered_bars = []
        for bar in bars_bb:
            for staff_idx, staff in enumerate(staff_bb):
                staff_check = __within_bb_check(bar, staff)
                if staff_check == True:
                    # print 'BAR POSITION: {0}'.format(staff)
                    numbered_bars.append((staff[0], bar[1], staff[2], bar[3], staff[4]))
        return numbered_bars
        


    def _bar_sorting(self, bar_vector):
        """
        Sorts a set of bars according to their staff number and x-position. Input vector should be:
        [staff_no, ux, uy, lx, ly]
        """
        checked_bars = sorted(bar_vector, key = lambda element: (element[0], element[1]))
        # lg.debug(checked_bars)
        return checked_bars

    def _system_structure_parser(self, system_input):
        """
        Parses the structure of the system according to the user input
        """
        system = system_input.split(',')
        output = []
        for i, s in enumerate(system):
            for j in range(int(s)):
                output.append(i+1)
        return output
    
    def _parse_staff_hint(self, sg_hint):
        # parse staff group hint to generate staff group
        sg_hint = sg_hint.split(" ")
        systems = []
        for s in sg_hint:
            parser = nestedExpr()
            sg_list = parser.parseString(s).asList()[0]
            staff_grp, n = self._create_staff_group(sg_list, MeiElement('staffGrp'), 0)

            # parse repeating staff groups (systems)
            num_sb = 1
            match = re.search('(?<=x)(\d+)$', s)
            if match is not None:
                # there are multiple systems of this staff grouping
                num_sb = int(match.group(0))
            
            for i in range(num_sb):
                systems.append(staff_grp)

        return systems

    def _create_staff_group(self, sg_list, staff_grp, n):
        '''
        Recursively create the staff group element from the parsed
        user input of the staff groupings
        '''
        if not sg_list:
            return staff_grp, n
        else:
            if type(sg_list[0]) is list:
                new_staff_grp, n = self._create_staff_group(sg_list[0], MeiElement('staffGrp'), n)
                staff_grp.addChild(new_staff_grp)
            else:
                # check for barthrough character
                if sg_list[0][-1] == '|':
                    # the barlines go through all the staves in the staff group
                    staff_grp.addAttribute('barthru', 'true')
                    # remove the barthrough character, should now only be an integer
                    sg_list[0] = sg_list[0][:-1]

                n_staff_defs = int(sg_list[0])
                # get current staffDef number
                for i in range(n_staff_defs):
                    staff_def = MeiElement('staffDef')
                    staff_def.addAttribute('n', str(n+i+1))
                    staff_grp.addChild(staff_def)
                n += n_staff_defs

            return self._create_staff_group(sg_list[1:], staff_grp, n)

    def _highlight(self, image, ccs_bars):
        RGB_image = image.to_rgb()
        for c in ccs_bars:
            RGB_image.highlight(c[0], RGBPixel(255, 0, 0))
        return RGB_image 

    def process_file(self, image, sg_hint):
        # parse the staff group hint into a list of staffGrps---one for each system
        # [staffGrps, ...]
        system_staff_groups = self._parse_staff_hint(sg_hint)
        barfinder_sg_hint = ", ".join([str(len(sg.getDescendantsByName('staffDef'))) for sg in system_staff_groups])
        system = self._system_structure_parser(barfinder_sg_hint)
        # print  system #GVM
        # Returns the vertices for each staff and its number
        stf_position = self._staff_line_position(image)
        
        if len(stf_position) != len(system):
            print 'Number of recognized staves is different to the one entered by the user'

        # Appends the proper system number according to the user input
        for i, s in enumerate(stf_position):
            stf_position[i].append(system[i])

        staff_bb = []
        # Saving staff bounding boxes
        for st in stf_position:
            staff_bb.append([st[0], st[1], st[2], st[3], st[4]])
        # print stf_position, '\n' #GVM
        # print staff_bb, '\n' #GVM
        # Staff-line removal
        no_staff_image = self._staffline_removal(image)
        self._despeckle(no_staff_image)

        # Filters short-runs
        mfr = image.most_frequent_run('black', 'vertical')
        filtered_image = self._most_frequent_run_filter(no_staff_image, mfr)    # most_frequent_run

        # cc's and highlighs no staff and shrot runs filtered image and writes txt file with candidate bars
        ccs_bars = self._ccs(filtered_image)
        checked_bars = self._bar_candidate_check(ccs_bars, stf_position, system)
        # print 'CHECKED_BARS:{0}'.format(checked_bars)
        
        #RGB_image = self._highlight(image, checked_bars)
        #output_path = os.path.splitext(input_file.split('/')[-1])[0] + '_candidates.tiff'
        #RGB_image.save_tiff(output_path) #GVM
        # RGB_image.save_tiff('./output_images/C_07a_ED-Kl_1_A-Wn_SHWeber90_S_009_bars.tiff') 
        bar_list = []
        # print "CHECKED_BARS: {0}\n\n".format(checked_bars) #GVM
        for c in checked_bars:
            bar_list.append([c[1], c[0].offset_x, c[0].offset_y, c[0].offset_x+c[0].ncols-1, c[0].offset_y+c[0].nrows-1])

        sorted_bars = self._bar_sorting(bar_list)
        # print '\nSTAFF_BB:{0}\n\nBAR_BB:{1}\n'.format(staff_bb, sorted_bars)

        numbered_bars = self._staff_number_assign(sorted_bars, staff_bb)
        # for nb in numbered_bars:
        #     print nb
        return staff_bb, numbered_bars 
