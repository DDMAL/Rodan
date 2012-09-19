from gamera.core import *
from gamera.toolkits import musicstaves, lyric_extraction, border_removal
from gamera import classify
from gamera import knn
import PIL, os
import argparse

from meicreate import BarlineDataConverter
from pymei import MeiElement
import re
from pyparsing import nestedExpr

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
        system_position = []
        system_position.append(stf_position[0])
        for j, s in enumerate(stf_position[1:]):
            if s[5] != system_position[-1][5]:
                system_position[-1].pop(3)
                system_position[-1].insert(3, stf_position[j][3])
                system_position[-1].pop(4)
                system_position[-1].insert(4, stf_position[j][4])
                system_position.append(s)    
        system_position[-1].pop(3)
        system_position[-1].insert(3, stf_position[-1][3])
        system_position[-1].pop(4)
        system_position[-1].insert(4, stf_position[-1][4])
        
        # lg.debug("system_position:\n{0}".format(system_position))
        return system_position

    def _bar_candidate_check(self, bar_candidates, stf_position):
        """
        Several methods to discard and/or validate bar candidates:

        1) Checks if the candidate bars lie within the upper and lower 
        boundaries of each staff. 

        2) Checks if bar candidate upper o lower position lies within a stf_position

        3) Creates a barline at the beginning of each staff according 
        to the staff position by the Miyao staff finder.

        Returns a vector in the form: [[gameracore.Image, staff_no]]
        """

        # lg.debug("SP: {0}".format(stf_position))
        checked_bars = []
        stf_height = sum([i[4]-i[2] for i in stf_position])/len(stf_position)
        # lg.debug("stf_height:{0}".format(stf_height))

        # retrieves the position of the systems
        system_position = self._system_position_parser(stf_position)    
        # lg.debug("system_position:\n{0}".format(system_position))

        for bc in bar_candidates:
            passes = True

            # discards a candidate if its mean y-position is above or below the first and last staff
            if bc.offset_y + ( bc.nrows - 1 ) / 2 < stf_position[0][2] or \
               bc.offset_y + ( bc.nrows - 1 ) / 2 > stf_position[len(stf_position) - 1][4]: 
                continue 

            # discards a candidate if it lies at the left of the closest staff
            for j, sp in enumerate(stf_position):
                if bc.offset_y > sp[2]:
                    continue
                elif bc.offset_x < stf_position[j-1][1]:
                    passes = False
                    # lg.debug("Discarded {0} SP:{1}".format(bc, stf_position[j-1][1]))
                    break
                else:
                    break

            # Checks if bar candidate ul position lies within a stf_position
            for k, sp in enumerate(stf_position):
                passes = False
                if sp[2]-stf_height/8 < bc.offset_y < sp[4]+stf_height/8 or\
                    sp[2]-stf_height/8 < bc.offset_y + bc.nrows - 1 < sp[4]+stf_height/8:
                    passes = True
                    break

            if passes == True:      
                checked_bars.append([bc, j+1])

        # Inserts bars at the beginning of each staff according to the staff x-position
        # for stf in stf_position:
        #     image = Image((stf[1], stf[2]), (stf[1]+5, stf[4]))
        #     image.draw_filled_rect((stf[1], stf[2]), (stf[1]+5, stf[4]), 1)
        #     checked_bars.append([image, stf[0]])

        return checked_bars 

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

    def process_file(self, image, sg_hint):
        # parse the staff group hint
        system_staff_groups = self._parse_staff_hint(sg_hint)
        barfinder_sg_hint = ", ".join([str(len(sg.getDescendantsByName('staffDef'))) for sg in system_staff_groups])
        system = self._system_structure_parser(barfinder_sg_hint)

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

        # Staff-line removal
        no_staff_image = self._staffline_removal(image)
        self._despeckle(no_staff_image)

        # Filters short-runs
        mfr = image.most_frequent_run('black', 'vertical')
        filtered_image = self._most_frequent_run_filter(no_staff_image, mfr)    # most_frequent_run

        # cc's and highlighs no staff and shrot runs filtered image and writes txt file with candidate bars
        ccs_bars = self._ccs(filtered_image)
        checked_bars = self._bar_candidate_check(ccs_bars, stf_position)
        bar_bb = []

        bar_list = []
        for c in checked_bars:
            bar_list.append([c[1], c[0].offset_x, c[0].offset_y, c[0].offset_x+c[0].ncols-1, c[0].offset_y+c[0].nrows-1])

        sorted_bars = self._bar_sorting(bar_list)

        return staff_bb, sorted_bars
