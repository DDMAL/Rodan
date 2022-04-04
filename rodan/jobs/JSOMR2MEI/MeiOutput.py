import sys, json
from pymei import MeiDocument, MeiElement, documentToText

class MeiOutput(object):

    SCALE = ['c', 'd', 'e', 'f', 'g', 'a', 'b']

    def __init__(self, incoming_data, **kwargs):
        self.incoming_data = incoming_data
        self.mei_version = kwargs['mei_version']

        # for storing during generation
        self.surface = False

        # for grouping
        self.avg_punc_width = self._avg_punctum(list(filter(lambda g: g['glyph']['name'] == 'neume.punctum', incoming_data['glyphs'])))
        self.max_neume_spacing = kwargs['max_neume_spacing']
        self.max_group_size = kwargs['max_group_size']

        # nc interpolating
        self.lig_width = 2  # width of ligature in whole punctums

    ####################
    # Public Functions
    ####################

    def run(self):
        return self._createDoc()

    #####################
    # Utility Functions
    #####################

    def _add_attributes(self, el, attributes):
        for a in attributes:
            if attributes[a]:
                el.addAttribute(a, attributes[a])

    def _avg_punctum(self, punctums):

        width_sum = 0
        for p in punctums:
            width_sum += p['glyph']['bounding_box']['ncols']
        return width_sum / len(punctums)

    ##################
    # MEI Generators
    ##################

    def _createDoc(self):
        doc = self._generate_doc()

        return documentToText(doc)

    def _generate_doc(self):
        meiDoc = MeiDocument()
        self._generate_mei(meiDoc)

        return meiDoc

    def _generate_mei(self, parent):
        el = MeiElement("mei")
        parent.root = el

        el.addAttribute("meiversion", self.mei_version)

        self._generate_meiHead(el)
        self._generate_music(el)

    def _generate_meiHead(self, parent):
        el = MeiElement("meiHead")
        parent.addChild(el)

    def _generate_music(self, parent):
        el = MeiElement("music")
        parent.addChild(el)

        self._generate_facsimile(el)
        self._generate_body(el)

    def _generate_facsimile(self, parent):
        el = MeiElement("facsimile")
        parent.addChild(el)

        self._generate_surface(el)

    def _generate_surface(self, parent):
        el = MeiElement("surface")
        parent.addChild(el)

        attribs = {
            'ulx': str(self.incoming_data['page']['bounding_box']['ulx']),
            'uly': str(self.incoming_data['page']['bounding_box']['uly']),
            'lrx': str(self.incoming_data['page']['bounding_box']['ncols']),
            'lry': str(self.incoming_data['page']['bounding_box']['nrows']),
        }

        self._add_attributes(el, attribs)
        self.surface = el

    def _generate_zone(self, parent, bounding_box):
        (nrows, ulx, uly, ncols) = bounding_box.values()

        el = MeiElement("zone")
        parent.addChild(el)

        attribs = {
            'ulx': str(ulx),
            'uly': str(uly),
            'lrx': str(ulx + ncols),
            'lry': str(uly + nrows),
        }

        self._add_attributes(el, attribs)

        return el.getId()   # returns the facsimile reference id

    def _generate_body(self, parent):
        el = MeiElement("body")
        parent.addChild(el)

        self._generate_mdiv(el)

    def _generate_mdiv(self, parent):
        el = MeiElement("mdiv")
        parent.addChild(el)

        self._generate_score(el)

    def _generate_score(self, parent):
        el = MeiElement("score")
        parent.addChild(el)

        self._generate_scoreDef(el)
        self._generate_section(el)

    def _generate_scoreDef(self, parent):
        el = MeiElement("scoreDef")
        parent.addChild(el)

        self._generate_staffGrp(el)

    def _generate_staffGrp(self, parent):
        el = MeiElement("staffGrp")
        parent.addChild(el)

        self._generate_staffDef(el)

    def _generate_staffDef(self, parent):
        el = MeiElement("staffDef")
        parent.addChild(el)

        el.addAttribute('n', '1')   # use first staff parameters
        el.addAttribute('lines', str(self.incoming_data['staves'][0]['num_lines']))
        el.addAttribute('notationtype', 'neume')
        el.addAttribute('clef.line', '3')
        el.addAttribute('clef.shape', 'C')

    def _generate_section(self, parent):
        el = MeiElement("section")
        parent.addChild(el)

        for s in self.incoming_data['staves']:
            self._generate_staff(el, s)     # generate each staff

    def _generate_staff(self, parent, staff):
        el = MeiElement("staff")
        parent.addChild(el)

        zoneId = self._generate_zone(self.surface, staff['bounding_box'])
        el.addAttribute('facs', zoneId)
        el.addAttribute('n', str(staff['staff_no']))
        el.addAttribute('lines', str(staff['num_lines']))
        el.addAttribute('line_positions', str(staff['line_positions']))

        self._generate_layer(el)

    def _generate_layer(self, parent):
        el = MeiElement("layer")
        parent.addChild(el)

        # get all glyphs on THIS staff
        glyphs = list(filter(lambda g: g['pitch']['staff'] ==
                             el.getParent().getAttribute('n').value
                             and g['glyph']['name'].split('.')[0] != 'skip',
                             self.incoming_data['glyphs']))

        # process all glyphs
        processedGroupedGlyphs = self._process_glyphs(glyphs)

        # print('\n\n', el.getParent().getAttribute('n').value)
        for groupedGlyph in processedGroupedGlyphs:
            glyph = groupedGlyph[0]   # define first glyph
            glyphName = glyph['glyph']['name'].split('.')[0]

            # print(glyph['glyph']['bounding_box']['ulx'], glyph['glyph']['name'])
            if glyphName == 'accid':
                self._generate_accidental(el, glyph)
            elif glyphName == 'clef':
                self._generate_clef(el, glyph)
            elif glyphName == 'custos':
                self._generate_custos(el, glyph)
            elif glyphName == 'division':
                self._generate_division(el, glyph)
            elif glyphName == 'neume':
                self._generate_syllable(el, groupedGlyph)

    def _generate_comment(self, parent, text):
        el = MeiElement("_comment")
        el.setValue(str(text))
        parent.addChild(el)

    ####################
    # Glyph Generation
    ####################

    def _generate_accidental(self, parent, glyph):
        el = MeiElement("accid")
        parent.addChild(el)

        zoneId = self._generate_zone(self.surface, glyph['glyph']['bounding_box'])
        el.addAttribute('facs', zoneId)
        el.addAttribute("accid", glyph['glyph']['name'].split('.')[1])

    def _generate_clef(self, parent, glyph):
        el = MeiElement("clef")
        parent.addChild(el)

        el.addAttribute('shape', str(glyph['glyph']['name'].split('.')[1].upper()))
        el.addAttribute('line', str(glyph['pitch']['strt_pos']))

        zoneId = self._generate_zone(self.surface, glyph['glyph']['bounding_box'])
        el.addAttribute('facs', zoneId)

    def _generate_custos(self, parent, glyph):
        el = MeiElement("custos")
        parent.addChild(el)

        zoneId = self._generate_zone(self.surface, glyph['glyph']['bounding_box'])
        el.addAttribute('facs', zoneId)
        el.addAttribute("oct", str(glyph['pitch']['octave']))
        el.addAttribute("pname", str(glyph['pitch']['note']))

    def _generate_division(self, parent, glyph):
        el = MeiElement("division")
        parent.addChild(el)

        zoneId = self._generate_zone(self.surface, glyph['glyph']['bounding_box'])
        el.addAttribute('facs', zoneId)
        el.addAttribute("form", glyph['glyph']['name'].split('.')[1])

    def _generate_syllable(self, parent, glyphs):
        el = MeiElement("syllable")
        parent.addChild(el)

        # self._generate_syl(el, glyph)
        self._generate_comment(el, ', '.join('.'.join(n['glyph']['name'].split('.')[1:]) for n in glyphs))
        self._generate_neume(el, glyphs)

    def _generate_neume(self, parent, glyphs):
        el = MeiElement("neume")
        parent.addChild(el)

        for g in glyphs:
            self._generate_nc(el, g)

    def _generate_nc(self, parent, glyph):
        el = MeiElement("nc")
        parent.addChild(el)

        name = glyph['glyph']['name'].split('.')
        pitch = [glyph['pitch']['note'], glyph['pitch']['octave'], glyph['pitch']['clef'].split('.')[1]]
        bounding_box = None

        singular = len(name) < 3
        zoneId = False

        # print('\n', name, glyph['pitch']['staff'])

        # if one primative, bounding box already exists
        if singular:
            bounding_box = glyph['glyph']['bounding_box']
            zoneId = self._generate_zone(self.surface, bounding_box)
            el.addAttribute('facs', zoneId)

        # otherwise, interpolate bounding_boxes for each nc
        else:
            bounding_boxes = self._get_zonified_bounding_boxes(glyph)
            bounding_box = bounding_boxes[0]
            zoneId = self._generate_zone(self.surface, bounding_box)
            el.addAttribute('facs', zoneId)

        self._complete_primitive(name[1], parent, el, pitch, bounding_box)

        if not singular:
            self._generate_nc_rec(parent, self._get_relative_pitch(pitch, name[1]), name[2:], bounding_boxes[1:])

    def _generate_nc_rec(self, parent, pitch, acc, bounding_boxes):
        el = MeiElement("nc")
        parent.addChild(el)

        # print(bounding_boxes[0])
        bounding_box = bounding_boxes[0]
        zoneId = self._generate_zone(self.surface, bounding_box)
        el.addAttribute('facs', zoneId)

        newPitch = self._get_new_pitch(pitch, acc[0][0], acc[0][1])
        self._complete_primitive(acc[1], parent, el, newPitch, bounding_box)

        if acc[2:]:  # recursive step
            self._generate_nc_rec(parent, self._get_relative_pitch(newPitch, acc[1]), acc[2:], bounding_boxes[1:])

    ########################
    # Generation Utilities
    ########################

    def _complete_primitive(self, name, parent, el, pitch, bounding_box):
        el.addAttribute('pname', str(pitch[0]))
        el.addAttribute('oct', str(pitch[1]))

        if 'punctum' in name:
            pass

        elif 'inclinatum' in name:
            if self.mei_version is '4.0.0':
                el.addAttribute('tilt', 'se')
            else:
                el.addAttribute('name', 'inclinatum')

        elif 'ligature' in name:
            if self.mei_version is '4.0.0':
                el.addAttribute('ligated', 'true')
            else:
                el.addAttribute('ligature', 'true')

            # generate second part of ligature
            el2 = MeiElement("nc")
            parent.addChild(el2)
            relativePitch = self._get_relative_pitch(pitch, name)

            zoneId = self._generate_zone(self.surface, bounding_box)
            el2.addAttribute('facs', zoneId)

            el2.addAttribute('pname', relativePitch[0])
            el2.addAttribute('oct', relativePitch[1])
            if self.mei_version is'4.0.0':
                el2.addAttribute('ligated', 'true')
            else:
                el2.addAttribute('ligature', 'true')

    ##################
    # Complex Neumes
    ##################

    def _get_new_pitch(self, startPitch, contour, interval):
        (startNote, startOctave, clef) = startPitch

        startOctave = int(startOctave)
        interval = int(interval) - 1  # because intervals are 1 note off
        SCALE = self.SCALE

        if contour == 'u':      # upwards
            newOctave = startOctave + \
                int((SCALE.index(startNote) + interval) / len(SCALE))
            newNote = SCALE[(SCALE.index(startNote) + interval) % len(SCALE)]

        elif contour == 'd':    # downwards
            newOctave = startOctave - \
                int((len(SCALE) - SCALE.index(startNote) - 1 + interval) / len(SCALE))
            newNote = SCALE[(SCALE.index(startNote) - interval) % len(SCALE)]

        elif contour == 's':   # repetition
            newOctave = startOctave
            newNote = startNote

        return [newNote, str(newOctave), clef]

    def _get_relative_pitch(self, pitch, name):
        if 'ligature' in name:   # if ligature, find/return lower pitch
            return self._get_new_pitch(pitch, 'd', name.split('ligature')[1])
        else:
            return pitch

    #########################
    # Zonify Bounding Boxes
    #########################

    def _get_zonified_bounding_boxes(self, glyph):

        # print(glyph)
        bounding_box = glyph['glyph']['bounding_box']
        num_ncs = int(len(glyph['glyph']['name'].split('.')) / 2)

        name = glyph['glyph']['name'].split('.')
        nc_names = list(name[2 * i: (2 * i) + 2] for i in range(0, num_ncs))

        contours = self._find_numeric_contours(nc_names)
        zone_pos = self._find_zone_positions(nc_names, contours)

        x_min, x_max, y_min, y_max = self._find_zone_edges(nc_names, contours)
        x_dim = x_max
        y_dim = y_max - y_min
        zone_bounding = (x_dim, y_dim)

        bounding_boxes = self._translate_zone_pos_to_bounding_boxes(zone_pos, zone_bounding, bounding_box)

        # print('\n\n')

        return bounding_boxes

    def _translate_zone_pos_to_bounding_boxes(self, zone_pos, zone_bounding, glyph_bounding):
        bounding_boxes = []
        x_dim, y_dim = zone_bounding        # x_dim relates to ncols, y_dim relates to nrows
        ncols = glyph_bounding['ncols']
        nrows = glyph_bounding['nrows']
        if not self._zone_pos_is_positive(zone_pos):
            zone_pos = self._shift_zone_pos_positive(zone_pos)

        for nc in zone_pos:
            bounding_box = {
                'nrows': int(nrows * (nc[3] - nc[1]) / y_dim),
                'ulx': int(ncols * (nc[0] / x_dim)) + glyph_bounding['ulx'],
                'uly': int(nrows * (nc[1] / y_dim)) + glyph_bounding['uly'],
                'ncols': int(ncols * (nc[2] - nc[0]) / x_dim),
            }
            bounding_boxes.append(bounding_box)

        #     print(nc)
        #     print(bounding_box)

        # print(x_dim, y_dim)
        # print(glyph_bounding['ulx'], glyph_bounding['uly'], glyph_bounding['ncols'], glyph_bounding['nrows'])
        return bounding_boxes

    def _find_numeric_contours(self, nc_names):
        contours = [0]
        for x in nc_names:

            if 'ligature' in x[1]:
                contours.append(-(int(x[1].split('ligature')[1]) - 1))

            if x[0][0] == 'u':
                contours.append(int(x[0][1:]) - 1)
            elif x[0][0] == 'd':
                contours.append(-(int(x[0][1:]) - 1))
            elif x[0][0] == 's':
                contours.append(0)

        return contours

    def _find_zone_positions(self, nc_names, contours):

        # returns a 'relative' bounding_box for each nc
        zone_pos = []
        nudge = 0   # each lig requires a contour indices nudge

        # get relative bounding box of first nc
        r_ulx = 0
        r_uly = 0

        # need to do first glyph manually
        if 'ligature' in nc_names[0][1]:
            r_lrx = r_ulx + self.lig_width
            r_lry = r_uly - contours[1] + 1
            nudge += 1
        else:
            r_lrx = r_ulx + 1
            r_lry = r_uly + 1
        zone_pos.append([r_ulx, r_uly, r_lrx, r_lry])

        # print(nc_names, contours)
        # print(zone_pos)
        # get the rest relative to the first
        for i, nc in enumerate(nc_names[1:]):
            r_ulx = r_lrx
            r_uly = r_lry - contours[i + nudge + 1] - 1

            # find lrx, lry
            if 'ligature' in nc[1]:
                r_lrx = r_ulx + self.lig_width
                r_lry = r_uly - contours[i + nudge + 1]
                nudge += 1
            else:
                r_lrx = r_ulx + 1
                r_lry = r_uly + 1

            zone_pos.append([r_ulx, r_uly, r_lrx, r_lry])
            # print(zone_pos)

        return zone_pos

    def _find_zone_edges(self, nc_names, contours):
        # find boundaries of facs zone relative per glyph
        # i.e. punctum/inclinatum gets 1x1, ligature2 gets 2x2

        x_dim_max = sum((self.lig_width if 'ligature' in x[1] else 1) for x in nc_names)

        y_dim_min = 0
        y_dim_max = 0
        flow = 0
        for n in contours:
            flow += n
            if flow < y_dim_min:
                y_dim_min = flow
            if flow > y_dim_max:
                y_dim_max = flow

        return 0, x_dim_max, y_dim_min, y_dim_max + 1

    def _shift_zone_pos_positive(self, zone_pos):
        negative = True
        while negative:
            self._shift_zone_pos_by1(zone_pos)
            if self._zone_pos_is_positive(zone_pos):
                negative = False

        return zone_pos

    def _shift_zone_pos_by1(self, zone_pos):
        for i, z in enumerate(zone_pos):
            for j, num in enumerate(z):
                if j == 1 or j == 3:
                    zone_pos[i][j] += 1

    def _zone_pos_is_positive(self, zone_pos):
        for z in zone_pos:
            for num in [z[1], z[3]]:
                if num < 0:
                    return False
        return True

    ############################
    # Neume Grouping Utilities
    ############################

    def _process_glyphs(self, glyphs):

        # separate glyphs by type
        neumes = list(filter(lambda g: g['glyph']['name'].split('.')[0] == 'neume', glyphs))
        notNeumes = list(filter(lambda g: g['glyph']['name'].split('.')[0] != 'neume', glyphs))

        # group neume componenets
        neumesGrouped = self._group_neumes(neumes, int(self.avg_punc_width * self.max_neume_spacing), self.max_group_size)
        sortedGlyphs = []

        while neumesGrouped or notNeumes:
            # place the rest at the end
            if not notNeumes:
                sortedGlyphs.append(neumesGrouped[0])
                del neumesGrouped[0]
            elif not neumesGrouped:
                sortedGlyphs.append([notNeumes[0]])
                del notNeumes[0]

            # place in order
            elif notNeumes[0]['glyph']['bounding_box']['ulx'] <= neumesGrouped[0][0]['glyph']['bounding_box']['ulx']:
                sortedGlyphs.append([notNeumes[0]])
                del notNeumes[0]
            else:
                sortedGlyphs.append(neumesGrouped[0])
                del neumesGrouped[0]

        # print('\n\n')
        # for group in sortedGlyphs:
        #     for g in group:
        #         print(g['glyph']['bounding_box']['ulx'], g['glyph']['name'])

        return sortedGlyphs

    def _group_neumes(self, neumes, max_distance, max_group_size):
        # input a horizontal staff of neumes
        # output grouped neume components

        groupedNeumes = list([n] for n in neumes)
        edges = self._get_edges(neumes)

        self._auto_merge('inclinatum', 'left', groupedNeumes, edges)
        self._auto_merge('ligature', 'right', groupedNeumes, edges)
        self._auto_merge_if(max_distance, max_group_size, groupedNeumes, edges, self._get_edge_distance(edges))

        # self._print_neume_groups(groupedNeumes)

        return groupedNeumes

    def _get_edges(self, glyphs):
        return list([g['glyph']['bounding_box']['ulx'], g['glyph']['bounding_box']['ulx'] + g['glyph']['bounding_box']['ncols']] for g in glyphs)

    def _get_edge_distance(self, edges):
        return list([e[0] - edges[i][1], edges[i + 2][0] - e[1]] for i, e in enumerate(edges[1: -1]))

    def _auto_merge_if(self, pixelDistance, maxSize, neumeGroup, edges, edgeDistances):
        rangeArray = range(len(neumeGroup) - 2)
        nudge = -1

        for i in rangeArray:
            if edgeDistances[i][0] < pixelDistance\
                    and not len(neumeGroup[i - nudge]) + 1 > maxSize:
                self._mergeLeft(neumeGroup, edges, i - nudge)
                nudge += 1

    def _auto_merge(self, condition, direction, neumeGroup, edges):
        # merge every neume of type condition
        if direction == 'left':
            rangeArray = range(len(neumeGroup))
        else:
            rangeArray = range(len(neumeGroup) - 1, -1, -1)

        nudge = 0
        for i in rangeArray:
            n = neumeGroup[i - nudge][0]
            name = n['glyph']['name'].split('.')

            if direction == 'left'\
                    and condition in name[1]\
                    and i > 0:
                self._mergeLeft(neumeGroup, edges, i - nudge)
                nudge += 1

            elif direction == 'right'\
                    and condition in name[len(name) - 1]\
                    and i < rangeArray[0]:
                self._mergeRight(neumeGroup, edges, i - nudge)

    def _mergeRight(self, neumes, edges, pos):
        neumes[pos + 1] = neumes[pos] + neumes[pos + 1]
        edges[pos + 1][0] = edges[pos][0]
        del neumes[pos]
        del edges[pos]

    def _mergeLeft(self, neumes, edges, pos):
        neumes[pos - 1] += neumes[pos]
        edges[pos - 1][1] = edges[pos][1]
        del neumes[pos]
        del edges[pos]

    def _print_neume_groups(self, neumeGroups):
        print('\n\nStaff')
        for ng in neumeGroups:
            print('')
            for n in ng:
                print(n['glyph']['name'], n['pitch']['note'], n['pitch']['octave'])


if __name__ == "__main__":

    if len(sys.argv) == 2:
        (tmp, inJSOMR) = sys.argv
    else:
        print("incorrect usage\npython3 main.py")
        quit()

    with open(inJSOMR, 'r') as file:
        jsomr = json.loads(file.read())

    kwargs = {
        'mei_version': '4.0.0',
        'max_neume_spacing': 0.3,
        'max_group_size': 8,
    }

    mei_obj = MeiOutput(jsomr, **kwargs)
    mei_string = mei_obj.run()

    with open('output.mei', 'w') as file:
        file.write(mei_string)

    print("ran")
