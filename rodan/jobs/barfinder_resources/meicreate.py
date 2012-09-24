"""
Copyright (c) 2012, Gregory Burlet
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Sample usage:
python meicreate.py -b C_07a_ED-Kl_1_A-Wn_SHWeber90_S_009_bar_position_2.txt -s C_07a_ED-Kl_1_A-Wn_SHWeber90_S_009_staff_vertices.txt -f detmoldbars.mei -g '(2|)x2 (4(2|))' -v    
"""

import argparse
from pyparsing import nestedExpr
import os
import re
import sys
import datetime

from pymei import MeiDocument, MeiElement, XmlExport

class BarlineDataConverter:
    '''
    Convert the output of the barline detection algorithm
    to MEI.
    '''

    def __init__(self, staff_bb, bar_bb):
        '''
        Initialize the converter
        '''

        self.staff_bb = staff_bb
        self.bar_bb = bar_bb

    def bardata_to_mei(self, sg_hint, image_path, image_width, image_height):
        '''
        Perform the data conversion to mei
        '''

        self.meidoc = MeiDocument()
        mei = MeiElement('mei')
        self.meidoc.setRootElement(mei)

        ###########################
        #         MetaData        #
        ###########################
        mei_head = self._create_header()
        mei.addChild(mei_head)

        ###########################
        #           Body          #
        ###########################
        music = MeiElement('music')
        body = MeiElement('body')
        mdiv = MeiElement('mdiv')
        score = MeiElement('score')
        score_def = MeiElement('scoreDef')
        section = MeiElement('section')

        # physical location data
        facsimile = MeiElement('facsimile')
        surface = MeiElement('surface')
        graphic = self._create_graphic(image_path, image_width, image_height)
        surface.addChild(graphic)

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

        # there may be hidden staves in a system
        # make the encoded staff group the largest number of staves in a system
        final_staff_grp = max(systems, key=lambda x: len(x.getDescendantsByName('staffDef')))

        mei.addChild(music)
        music.addChild(facsimile)
        facsimile.addChild(surface)
        
        # list of staff bounding boxes within a system
        staves = []
        for staff_bb in self.staff_bb:
            # get bounding box of the staff
            # parse bounding box integers
            #staff_bb = [int(x) for x in staff_bb]
            staves.append(staff_bb[1:])
        
        music.addChild(body)
        body.addChild(mdiv)
        mdiv.addChild(score)
        score.addChild(score_def)
        score_def.addChild(final_staff_grp)
        score.addChild(section)

        # parse barline data file [staffnum][barlinenum_ulx]
        barlines = []
        for i, bar in enumerate(self.bar_bb):
            staff_num = int(bar[0])
            ulx = bar[1]
            try:
                barlines[staff_num-1].append(ulx)
            except IndexError:
                barlines.append([ulx])

        staff_offset = 0
        n_measure = 1
        # for each system
        for s_ind, s in enumerate(systems):
            # measures in a system
            s_measures = []
            staff_defs = s.getDescendantsByName('staffDef')
            # for each staff in the system
            for i in range(len(staff_defs)):
                staff_num = staff_offset + i
                s_bb = staves[staff_num]
                # bounding box of the staff
                s_ulx = s_bb[0]
                s_uly = s_bb[1]
                s_lrx = s_bb[2]
                s_lry = s_bb[3]

                # for each barline on this staff
                staff_bars = barlines[staff_num]
                for n, b in enumerate(staff_bars):
                    # calculate bounding box of the measure
                    if n == 0:
                        m_ulx = s_ulx
                    else:
                        m_ulx = staff_bars[n-1]

                    m_uly = s_uly
                    m_lry = s_lry

                    if n == len(staff_bars)-1:
                        m_lrx = s_lrx
                    else:
                        m_lrx = b

                    # create staff element
                    zone = self._create_zone(m_ulx, m_uly, m_lrx, m_lry)
                    surface.addChild(zone)
                    if len(sg_hint) == 1 or len(staff_defs) == len(final_staff_grp.getDescendantsByName('staffDef')):
                        staff_n = str(i+1)    
                    else:
                        # take into consideration hidden staves
                        staff_n = i + self._calc_staff_num(len(staff_defs), [final_staff_grp])
                    
                    staff = self._create_staff(staff_n, zone)

                    try:
                        s_measures[n].addChild(staff)
                    except IndexError:
                        # create a new measure
                        measure = self._create_measure(str(n_measure))
                        s_measures.append(measure)
                        section.addChild(measure)
                        measure.addChild(staff)
                        n_measure += 1

            # calculate min/max of measure/staff bounding boxes to get measure zone
            self._calc_measure_zone(s_measures)

            staff_offset += len(staff_defs)

            # add a system break, if necessary
            if s_ind+1 < len(systems):
                sb = MeiElement('sb')
                section.addChild(sb)

    def _create_header(self, rodan_version='0.1'):
        '''
        Create a meiHead element
        '''

        mei_head = MeiElement('meiHead')
        today = datetime.date.today().isoformat()

        app_name = 'RODAN/barlineFinder'

        # file description
        file_desc = MeiElement('fileDesc')

        title_stmt = MeiElement('titleStmt')
        title = MeiElement('title')
        resp_stmt = MeiElement('respStmt')
        corp_name = MeiElement('corpName')
        corp_name.setValue('Distributed Digital Music Archives and Libraries Lab (DDMAL)')
        title_stmt.addChild(title)
        title_stmt.addChild(resp_stmt)
        resp_stmt.addChild(corp_name)
        
        pub_stmt = MeiElement('pubStmt')
        resp_stmt = MeiElement('respStmt')
        corp_name = MeiElement('corpName')
        corp_name.setValue('Distributed Digital Music Archives and Libraries Lab (DDMAL)')
        pub_stmt.addChild(resp_stmt)
        resp_stmt.addChild(corp_name)

        mei_head.addChild(file_desc)
        file_desc.addChild(title_stmt)
        file_desc.addChild(pub_stmt)

        # encoding description
        encoding_desc = MeiElement('encodingDesc')
        app_info = MeiElement('appInfo')
        application = MeiElement('application')
        application.addAttribute('version', rodan_version)
        name = MeiElement('name')
        name.setValue(app_name)
        ptr = MeiElement('ptr')
        ptr.addAttribute('target', 'https://github.com/DDMAL/barlineFinder')

        mei_head.addChild(encoding_desc)
        encoding_desc.addChild(app_info)
        app_info.addChild(application)
        application.addChild(name)
        application.addChild(ptr)

        # revision description
        revision_desc = MeiElement('revisionDesc')
        change = MeiElement('change')
        change.addAttribute('n', '1')
        resp_stmt = MeiElement('respStmt')
        corp_name = MeiElement('corpName')
        corp_name.setValue('Distributed Digital Music Archives and Libraries Lab (DDMAL)')
        change_desc = MeiElement('changeDesc')
        ref = MeiElement('ref')
        ref.addAttribute('target', '#'+application.getId())
        ref.setValue(app_name)
        ref.setTail('.')
        p = MeiElement('p')
        p.addChild(ref)
        p.setValue('Encoded using ')
        date = MeiElement('date')
        date.setValue(today)
        
        mei_head.addChild(revision_desc)
        revision_desc.addChild(change)
        change.addChild(resp_stmt)
        resp_stmt.addChild(corp_name)
        change.addChild(change_desc)
        change_desc.addChild(p)
        change.addChild(date)

        return mei_head

    def _calc_staff_num(self, num_staves, staff_grps):
        '''
        In the case where there are hidden staves,
        search for the correct staff number within the staff
        group definition.
        '''

        if len(staff_grps) == 0:
            # termination condition (or no match found)
            return 0
        else:
            sg_staves = staff_grps[0].getChildrenByName('staffDef')
            sgs = staff_grps[0].getChildrenByName('staffGrp')
            if num_staves == len(sg_staves):
                # no need to look at subsequent staff groups
                n = int(sg_staves[0].getAttribute('n').value)
            else:
                n = self._calc_staff_num(num_staves, sgs)

            return n + self._calc_staff_num(num_staves, staff_grps[1:])
        
    def _calc_measure_zone(self, measures):
        '''
        Calculate the bounding box of the provided measures
        by calculating the min and max of the bounding boxes
        of the staves which compose the measure.
        '''

        # for each measure
        for m in measures:
            staff_measure_zones = []
            min_ulx = sys.maxint
            min_uly = sys.maxint
            max_lrx = -sys.maxint - 1
            max_lry = -sys.maxint - 1
            for s in m.getChildrenByName('staff'):
                s_zone = self.meidoc.getElementById(s.getAttribute('facs').value)
                ulx = int(s_zone.getAttribute('ulx').value)
                if ulx < min_ulx:
                    min_ulx = ulx

                uly = int(s_zone.getAttribute('uly').value)
                if uly < min_uly:
                    min_uly = uly

                lrx = int(s_zone.getAttribute('lrx').value)
                if lrx > max_lrx:
                    max_lrx = lrx

                lry = int(s_zone.getAttribute('lry').value)
                if lry > max_lry:
                    max_lry = lry

            m_zone = self._create_zone(min_ulx, min_uly, max_lrx, max_lry)
            m.addAttribute('facs', m_zone.getId())
            surface = self.meidoc.getElementsByName('surface')[0]
            surface.addChild(m_zone)

    def _create_graphic(self, image_path, image_width, image_height):
        '''
        Create a graphic element.
        '''

        graphic = MeiElement('graphic')
        graphic.addAttribute('width', str(image_width))
        graphic.addAttribute('height', str(image_height))
        graphic.addAttribute('target', str(image_path))
        graphic.addAttribute('unit', 'px')

        return graphic

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

    def _create_staff(self, n, zone):
        '''
        Create a staff element, and attach a zone reference to it
        '''

        staff = MeiElement('staff')
        staff.addAttribute('n', str(n))
        staff.addAttribute('facs', zone.getId())

        return staff

    def _create_measure(self, n, zone = None):
        '''
        Create a measure element and attach a zone reference to it.
        The zone element is optional, since the zone of the measure is
        calculated once all of the staves within a measure have been added
        to the MEI.
        '''

        measure = MeiElement('measure')
        measure.addAttribute('n', str(n))

        if zone is not None:
            measure.addAttribute('facs', zone.getId())

        return measure

    def _create_zone(self, ulx, uly, lrx, lry):
        '''
        Create a zone element
        '''

        zone = MeiElement('zone')
        zone.addAttribute('ulx', str(ulx))
        zone.addAttribute('uly', str(uly))
        zone.addAttribute('lrx', str(lrx))
        zone.addAttribute('lry', str(lry))

        return zone

    def output_mei(self, output_path):
        '''
        Write the generated mei to disk
        '''

        # output mei file
        XmlExport.meiDocumentToFile(self.meidoc, output_path)

    def get_wrapped_mei(self):
        '''
        Return the generated mei document
        '''

        mw = MeiWrapper(self.meidoc)

        return mw

class MeiWrapper:
    def __init__(self, meidoc):
        self.md = meidoc
