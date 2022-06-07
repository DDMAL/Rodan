# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import numpy as np
import json
import parse_classifier_table as pct
from pymei import MeiDocument, MeiElement, MeiAttribute, documentToText, documentToFile
from itertools import groupby
from visualize_alignment import draw_mei_doc

try:
    from rodan.jobs.MEI_encoding import __version__
except ImportError:
    __version__ = "[Not encoded using Rodan]"


def add_flags_to_glyphs(glyphs):
    '''
    Given the raw list of glyphs from pitch-finding containing position and classification
    information, add some information to the data structure. This lets us tell more easily where
    line breaks are in the file without having to re-perform calculations.
    '''

    for g in glyphs:
        for key in g['glyph'].keys():
            g[key] = g['glyph'][key]
        for key in g['pitch'].keys():
            g[key] = g['pitch'][key]
        del g['pitch']
        del g['glyph']
        g['bounding_box']['lrx'] = g['bounding_box']['ulx'] + g['bounding_box']['ncols']
        g['bounding_box']['lry'] = g['bounding_box']['uly'] + g['bounding_box']['nrows']

    # sort glyphs in lexicographical order by staff #, left to right
    glyphs.sort(key=lambda x: (int(x['staff']), int(x['offset'])))

    temp1 = 0
    temp2 = 0
    for i in range(len(glyphs)-1):
        temp1 = glyphs[i]
        temp2 = glyphs[i+1]
        midpoint = (temp1['bounding_box']['lrx'] + temp1['bounding_box']['ulx']) / 2
        if temp2['bounding_box']['ulx'] < midpoint and temp2['bounding_box']['ulx'] >= temp1['bounding_box']['ulx']:
            if (temp1['bounding_box']['uly'] < temp2['bounding_box']['uly']):
                glyphs[i+1], glyphs[i] = temp1, temp2


    # add flag to every glyph denoting whether or not a line break should come immediately after
    for i in range(len(glyphs)):

        glyphs[i]['system_begin'] = False
        if i < len(glyphs) - 1:

            left_staff = int(glyphs[i]['staff'])
            right_staff = int(glyphs[i + 1]['staff'])

            if left_staff < right_staff:
                glyphs[i]['system_begin'] = True

    return glyphs


def neume_to_lyric_alignment(glyphs, syl_boxes, median_line_spacing):
    '''
    Given the processed glyphs from add_flags_to_glyphs and the information from the text alignment
    job (syl_boxes, median_line_spacing), finds out which syllables of text correspond to which
    glyphs on the page and returns a list of ([neumes], syllable) pairs.

    Things like custos, clefs, and accidentals are included inside these lists even though they
    are, strictly speaking, not part of the MEI for the syllable; that is handled in the method that
    actually encodes the MEI.
    '''

    dummy_syl = {u'syl': '', u'ul': [0, 0], u'lr': [0, 0]}

    # if there's no syl information then make fake syllables for testing. this method makes one
    # large syllable covering an entire staff line.
    if not syl_boxes:
        glyphs = sorted(glyphs, key=lambda x: int(x['staff']))

        grouped_glyphs = [list(g) for k, g in groupby(glyphs, key=lambda x: int(x['staff']))]

        pairs = [(g, dummy_syl) for g in grouped_glyphs]
        return pairs

    glyphs_pos = 0
    num_glyphs = len(glyphs)

    pairs = []
    starts = []
    last_used = 0
    for box in syl_boxes:

        # assign each syllable to an ANCHOR GLYPH.
        # for each syl_box, look for glyphs that
        # 1) have not been assigned to a syl_box yet, and
        # 2) are within a median line width above the current box, and
        # 3) are to the right of the current box.
        above_glyphs = [
            g for g in glyphs[last_used:] if
            (box['ul'][1] - median_line_spacing < g['bounding_box']['uly'] < box['ul'][1]) and
            (box['ul'][0] < g['bounding_box']['ulx'] + g['bounding_box']['ncols'] // 2)
            ]

        if not above_glyphs:
            starts.append(last_used)
            continue

        # find the glyph in above_glyphs that is closest to the current box
        nearest_glyph = min(above_glyphs, key=lambda g: g['bounding_box']['ulx'])

        # append the index of this glyph to the start positions list
        starts.append(glyphs.index(nearest_glyph))
        last_used = max(starts)

    # if there are unassigned "orphan" glyphs at the beginning of the page, assign them all to a
    # dummy syl_box so they can be detected later
    if not starts[0] == 0:
        pairs.append(
            (glyphs[:starts[0]], dummy_syl)
        )

    starts.append(len(glyphs))
    for i in range(len(starts) - 1):

        # it's possible that no glyphs are assigned to a syllable: in this case, just
        # get rid of the syllable altogether.
        glyph_range = glyphs[starts[i]:starts[i+1]]
        if not glyph_range:
            continue

        pair = (glyph_range, syl_boxes[i])
        pairs.append(pair)

    return pairs


def generate_base_document():
    '''
    Generates a generic template for an MEI document for neume notation.

    Currently a bit of this is hardcoded and should probably be made more customizable.
    '''
    meiDoc = MeiDocument("4.0.0")

    mei = MeiElement("mei")
    mei.addAttribute("meiversion", "4.0.0")
    meiDoc.root = mei

    # placeholder meiHead
    meihead = MeiElement('meiHead')
    mei.addChild(meihead)
    fileDesc = MeiElement('fileDesc')
    meihead.addChild(fileDesc)
    titleSt = MeiElement('titleStmt')
    fileDesc.addChild(titleSt)
    title = MeiElement('title')
    titleSt.addChild(title)
    title.setValue('MEI Encoding Output (%s)' % __version__)
    pubStmt = MeiElement('pubStmt')
    fileDesc.addChild(pubStmt)

    music = MeiElement("music")
    mei.addChild(music)

    facs = MeiElement("facsimile")
    music.addChild(facs)

    surface = MeiElement("surface")
    facs.addChild(surface)

    body = MeiElement('body')
    music.addChild(body)

    mdiv = MeiElement('mdiv')
    body.addChild(mdiv)

    score = MeiElement('score')
    mdiv.addChild(score)

    scoreDef = MeiElement('scoreDef')
    score.addChild(scoreDef)

    staffGrp = MeiElement('staffGrp')
    scoreDef.addChild(staffGrp)

    staffDef = MeiElement('staffDef')
    staffGrp.addChild(staffDef)

    # these hardcoded attributes define a single staff with 4 lines, neume notation, with a default c clef
    staffDef.addAttribute('n', '1')
    staffDef.addAttribute('lines', '4')
    staffDef.addAttribute('notationtype', 'neume')
    staffDef.addAttribute('clef.line', '3')
    staffDef.addAttribute('clef.shape', 'C')

    section = MeiElement('section')
    score.addChild(section)

    staff = MeiElement('staff')
    section.addChild(staff)

    layer = MeiElement('layer')
    staff.addChild(layer)

    return meiDoc, surface, layer


def add_attributes_to_element(el, add):
    '''
    A helper function that takes in a dictionary linking attributes --> values, and adds all these
    attributes to the libMEI object @add.
    '''
    for key in add.keys():
        if add[key] == 'None':
            continue
        el.addAttribute(key, str(add[key]))
    return el


def create_primitive_element(xml, glyph, idx, surface):
    '''
    Creates a "lowest-level" element out of the xml retrieved from the MEI mapping tool (passed as
    an ElementTree object in @xml) and registers its bounding box in the given surface.
    '''
    res = MeiElement(xml.tag)
    attribs = xml.attrib

    # ncs, custos do not have a @line attribute. this is a bit of a hack...
    if xml.tag == 'clef':
        attribs['line'] = str(glyph['strt_pos'])

    attribs['oct'] = str(glyph['octave'])
    attribs['pname'] = str(glyph['note'])
    res = add_attributes_to_element(res, attribs)


    if type(glyph['bounding_box']) == dict:
        zoneId = generate_zone(surface, glyph['bounding_box'])
    else:
        zoneId = generate_zone(surface, glyph['bounding_box'][idx])
    res.addAttribute('facs', '#' + zoneId)
    return res



def glyph_to_element(classifier, width_container, glyph, surface):
    '''
    Translates a glyph as output by the pitchfinder into an MEI element, registering bounding boxes
    in the given surface.

    Currently the assumption is that no MEI information in the given classifier is more than one
    level deep - that is, everything is either a single element (clef, custos) or the child of a
    single element (neumes). THIS IS NOT TRUE FOR ALL NEUMATIC NOTATION TYPES!
    '''
    name = str(glyph['name'])
    try:
        xml = classifier[name]
        width = width_container[name]
    except KeyError:
        print('entry {} not found in classifier table!'.format(name))
        return None

    # remove everything up to the first dot in the name of the glyph
    try:
        name = name[:name.index('.')]
    except ValueError:
        pass

    # if this is an element with no children, then just apply a pitch and position to it
    if not list(xml):
        return create_primitive_element(xml, glyph, 0, surface)

    # else, this element has at least one child (is a neume)
    ncs = list(xml)

    # divide bbox according to the width column
    bb_org = glyph['bounding_box']
    bb_new = []
    length_org = bb_org['lrx'] - bb_org['ulx']
    length_nc = length_org / len(width)
    # iterate the list
    for i in range(len(width)):
        # count down the element
        for j in range(width[i]):
            bb_temp = {
                'ulx': bb_org['ulx'] + i * length_nc,
                'uly': bb_org['uly'],
                'lrx': bb_org['lrx'] + (i+1) * length_nc,
                'lry': bb_org['uly'],
            }
            bb_new.append(bb_temp)
    glyph['bounding_box'] = bb_new

    els = []
    # els = [create_primitive_element(nc, glyph, surface) for nc in ncs]
    for i in range(len(ncs)):
        try:
            el = create_primitive_element(ncs[i], glyph, i, surface)
        except IndexError:
            print('Width column indicates {} neume components but gets {} neume components from input for classifier {}'.format(len(glyph['bounding_box']), len(ncs), str(glyph['name'])))
            continue
        els.append(el)

    parent = MeiElement(xml.tag)
    parent.setChildren(els)

    if len(els) < 2:
        return parent

    # if there's more than one element, must resolve intervals between ncs
    for i in range(1, len(els)):
        prev_nc = parent.children[i - 1]
        cur_nc = parent.children[i]
        new_pname, new_octave = resolve_interval(prev_nc, cur_nc)
        cur_nc.addAttribute('pname', new_pname)
        cur_nc.addAttribute('oct', new_octave)
        cur_nc.removeAttribute('intm')

    return parent


def resolve_interval(prev_nc, cur_nc):
    '''
    When given a ligature or something like that which specifies only the starting pitch and an
    interval, we need to calculate what the pitch of the rest of the notes are going to be. Given
    two neume components, where the second one has an 'intm' attribute, this calculates what the
    correct scale degree and octave is.

    N.B. in MEI octave numbers increase when going from a B to a C.
    '''

    scale = ['c', 'd', 'e', 'f', 'g', 'a', 'b']

    interval = cur_nc.getAttribute('intm').value
    try:
        interval = interval.lower().replace('s', '')
        interval = int(interval)
    except ValueError:
        interval = 0
    except AttributeError:
        interval = 0

    starting_pitch = prev_nc.getAttribute('pname').value
    starting_octave = int(prev_nc.getAttribute('oct').value)
    end_octave = starting_octave

    try:
        start_index = scale.index(starting_pitch)
    except ValueError:
        raise ValueError('pname {} is not in scale {}'.format(starting_pitch, scale))

    end_idx = start_index + interval

    if end_idx >= len(scale):
        end_octave += 1
    elif end_idx < 0:
        end_octave -= 1

    end_idx %= len(scale)
    end_pname = scale[end_idx]

    return str(end_pname), str(end_octave)


def generate_zone(surface, bb):
    '''
    Given a bounding box, generates a zone element, adds it to the given @surface,
    and returns its ID.
    '''
    el = MeiElement('zone')
    surface.addChild(el)

    # could be cleaner, but necessary so that we don't add extra attributes from @bb
    attribs = {
        'ulx': bb['ulx'],
        'uly': bb['uly'],
        'lrx': bb['lrx'],
        'lry': bb['lry'],
    }

    el = add_attributes_to_element(el, attribs)
    return el.getId()


def build_mei(pairs, classifier, width_container, staves, page):
    '''
    Encodes the final MEI document using:
        @pairs: Pairs from the neume_to_lyric_alignment.
        @classifier: The MEI mapping dictionary output
            by fetch_table_from_csv() in parse_classifier_table.py
        @width_container: The width column by fetch_table_from_csv() in parse_classifier_table.py
            the length of the list indicates the width of the neume,
            the sum of the list indicates the number of the ncs in the neume
        @staves: Bounding box information from pitch finding JSON.
        @page: Page dimension information from pitch finding JSON.
    '''
    meiDoc, surface, layer = generate_base_document()
    surface_bb = {
        'ulx': page['bounding_box']['ulx'],
        'uly': page['bounding_box']['uly'],
        'lrx': page['bounding_box']['ulx'] + page['bounding_box']['ncols'],
        'lry': page['bounding_box']['uly'] + page['bounding_box']['nrows']
    }
    surface.addAttribute('ulx', str(surface_bb['ulx']))
    surface.addAttribute('uly', str(surface_bb['uly']))
    surface.addAttribute('lrx', str(surface_bb['lrx']))
    surface.addAttribute('lry', str(surface_bb['lry']))

    # add an initial system beginning
    sb = MeiElement('sb')
    bb = staves[0]['bounding_box']
    bb = {
        'ulx': bb['ulx'],
        'uly': bb['uly'],
        'lrx': bb['ulx'] + bb['ncols'],
        'lry': bb['uly'] + bb['nrows'],
    }
    zoneId = generate_zone(surface, bb)
    sb.addAttribute('facs', '#' + zoneId)
    layer.addChild(sb)

    # add to the MEI document, syllable by syllable
    for gs, syl_box in pairs:

        # first add information about the text itself
        cur_syllable = MeiElement('syllable')
        bb = {
            'ulx': syl_box['ul'][0],
            'uly': syl_box['ul'][1],
            'lrx': syl_box['lr'][0],
            'lry': syl_box['lr'][1],
        }
        zoneId = generate_zone(surface, bb)
        layer.addChild(cur_syllable)

        # add syl element containing text on page
        syl = MeiElement('syl')
        syl.setValue(str(syl_box['syl']))
        syl.addAttribute('facs', '#' + zoneId)
        cur_syllable.addChild(syl)

        # iterate over glyphs on the page that fall within the bounds of this syllable
        for i, glyph in enumerate(gs):

            # are we done with neume components in this grouping?
            syllable_over = not any(('neume' in x['name']) for x in gs[i:])
            new_el = glyph_to_element(classifier, width_container, glyph, surface)
            if not new_el:
                continue
            # four cases to consider:
            # 1. no line break and done with this syllable (usually a clef)
            # 2. no line break and not done with this syllable (more neume components to add)
            # 3. a line break and done with this syllable (a custos OUTSIDE a <syllable> tag)
            # 4. a line break and not done with this syllable (a custos INSIDE a <syllable> tag)

            if not glyph['system_begin']:
                # case 1
                if syllable_over:
                    layer.addChild(new_el)
                # case 2
                else:
                    cur_syllable.addChild(new_el)
                continue

            sb = MeiElement('sb')
            cur_staff = int(glyph['staff'])

            bb = staves[cur_staff]['bounding_box']
            bb = {
                'ulx': bb['ulx'],
                'uly': bb['uly'],
                'lrx': bb['ulx'] + bb['ncols'],
                'lry': bb['uly'] + bb['nrows'],
            }
            zoneId = generate_zone(surface, bb)
            sb.addAttribute('facs', '#' + zoneId)

            # case 3: the syllable is over, so the custos goes outside the syllable
            # do not include custos in <sb> tags! this was a typo in the MEI documentation
            if syllable_over:
                layer.addChild(new_el)
                layer.addChild(sb)
            # case 4
            else:
                cur_syllable.addChild(new_el)
                cur_syllable.addChild(sb)

    return meiDoc


def merge_nearby_neume_components(meiDoc, width_mult):
    '''
    A heuristic to merge together neume components that are 1) consecutive 2) within the same
    syllable 3) within a certain distance from each other. This distance is by default set to the
    average width of a neume component within this page, but can be modified using the
    @width_multiplier argument. The output MEI will still be correct even if this method is not run.
    '''
    all_syllables = meiDoc.getElementsByName('syllable')
    surface = meiDoc.getElementsByName('surface')[0]

    surf_dict = {}
    neume_widths = []
    for c in surface.getChildren():
        surf_dict[c.id] = {}
        for coord in c.attributes:
            surf_dict[c.id][coord.name] = int(coord.value)


    neume_widths = [x['lrx'] - x['ulx'] for x in surf_dict.values()]
    med_neume_width = np.median(neume_widths) * width_mult

    # returns True if both inputs are of type 'neume' and they are close enough to be merged
    def compare_neumes(nl, nr):
        if not (nl.name == 'neume' and nr.name == 'neume'):
            return False

        nl_right_bound = max([surf_dict[n.getAttribute('facs').value[1:]]['lrx'] for n in nl.children])
        nr_left_bound = min([surf_dict[n.getAttribute('facs').value[1:]]['ulx'] for n in nr.children])

        distance = nr_left_bound - nl_right_bound

        return (distance <= med_neume_width)

    for syllable in all_syllables:
        children = syllable.getChildren()
        
        # holds children of the current syllable that will be added to target
        accumulator = []

        # holds the first neume in a sequence of neumes that will be merged
        target = None

        # holds children once in the accumulator that must be removed after iteration is done
        children_to_remove = []

        # iterate over all children. for each neume decide whether or not it should be merged
        # with the next one using compare_neumes. if yes, add the next one to the accumulator.
        # if not, empty the accumulator and add its contents to the target.
        for i in range(len(children)):
            if (i + 1 < len(children)) and (compare_neumes(children[i], children[i+1])):
                accumulator.append(children[i+1])
                if not target:
                    target = children[i]
            else:
                ncs_to_merge = []
                for neume in accumulator:           # empty contents of accumulator into ncs_to_merge
                    ncs_to_merge += neume.children
                for nc in ncs_to_merge:             # merge all neume components
                    target.addChild(nc)
                children_to_remove += accumulator
                # for neume in accumulator:           # clean up neumes that were merged
                #     syllable.removeChild(neume)
                target = None
                accumulator = []

        for neume in children_to_remove:
            syllable.removeChild(neume)

    return meiDoc


def process(jsomr, syls, classifier, width_mult, width_container,verbose=True):
    '''
    Runs the entire MEI encoding process given the three inputs to the rodan job and the
    width_multiplier parameter for merging neume components.
    '''
    glyphs = jsomr['glyphs']
    syl_boxes = syls['syl_boxes'] if syls is not None else None
    median_line_spacing = syls['median_line_spacing'] if syls is not None else None

    glyphs = add_flags_to_glyphs(glyphs)
    pairs = neume_to_lyric_alignment(glyphs, syl_boxes, median_line_spacing)
    meiDoc = build_mei(pairs, classifier, width_container, jsomr['staves'], jsomr['page'])

    if width_mult > 0:
        meiDoc = merge_nearby_neume_components(meiDoc, width_mult=width_mult)

    return documentToText(meiDoc)


if __name__ == '__main__':

    # A script for running the encoding process locally on the salzinnes manuscript.
    # Replace paths and filenames as per your local setup.
    # Assumes that all files are numbered with the "CF-" filenames that the images of the manuscript
    # originally came with.

    classifier_fname = 'csv-square notation test_20190725015554.csv'
    classifier, width_container = pct.fetch_table_from_csv(classifier_fname)

    f_inds = range(0, 200)

    for f_ind in f_inds:
        fname = 'salzinnes_{:0>3}'.format(f_ind)
        inJSOMR = './jsomr-split/pitches_{}.json'.format(fname)
        in_syls = './syl_json/{}.json'.format(fname)
        in_png = '/Users/tim/Desktop/PNG_compressed/CF-{:0>3}.png'.format(f_ind)
        out_fname = './out_mei/output_split_{}.mei'.format(fname)
        out_fname_png = './out_png/{}_alignment.png'.format(fname)

        try:
            with open(inJSOMR, 'r') as file:
                jsomr = json.loads(file.read())
            with open(in_syls) as file:
                syls = json.loads(file.read())
        except IOError:
            print('{} not found, skipping...'.format(fname))
            continue

        print('building mei for {}...'.format(fname))

        glyphs = jsomr['glyphs']
        syl_boxes = syls['syl_boxes']
        median_line_spacing = syls['median_line_spacing']

        print('adding flags to glyphs...')
        glyphs = add_flags_to_glyphs(glyphs)
        print('performing neume-to-lyric alignment...')
        pairs = neume_to_lyric_alignment(glyphs, syl_boxes, median_line_spacing)
        print('building MEI...')
        meiDoc = build_mei(pairs, classifier, width_container, jsomr['staves'], jsomr['page'])
        print('neume component spacing > 0, merging nearby components...')
        meiDoc = merge_nearby_neume_components(meiDoc, width_mult=0.25)

        #draw_mei_doc(in_png, out_fname_png, meiDoc)

        documentToFile(meiDoc, out_fname)
