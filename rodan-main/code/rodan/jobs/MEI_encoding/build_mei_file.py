# -*- coding: utf-8 -*-
from hashlib import new
from uuid import uuid4
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring #more concise?
import math
import numpy as np
import json
#from rodan.jobs.MEI_encoding import parse_classifier_table as pct #for rodan 
import parse_classifier_table as pct #---> for testing locally 
from itertools import groupby

try:
    from rodan.jobs.MEI_encoding import __version__
except ImportError:
    __version__ = "[Not encoded using Rodan]"


def new_el(name, p=None): 
    '''
    Create a new ElementTree Element with the given name and generate uuid4, with prefix 'm-'
    to conform with previous version
    '''
    if p is None: 
        element = ET.Element(name)
        element.set("xml:id", 'm-'+str(uuid4()))
        return element 
    else: 
        element = ET.SubElement(p, name)
        element.set("xml:id", 'm-'+str(uuid4()))
        return element

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
    #create document (eventually going to need to link a bunch of documents together 
    # under mei)


    mei = new_el("mei")
    mei.set("xmlns", "http://www.music-encoding.org/ns/mei")
    mei.set("meiversion", "5.0.0-dev")

    meiHead = new_el("meiHead", mei)

    fileDesc = new_el("fileDesc", meiHead)
    titleStmt = new_el("titleStmt", fileDesc)
    title = new_el("title", titleStmt)
    title.text = "MEI Encoding Output (1.0.0)"

    pubStmt = new_el("pubStmt", fileDesc)

    music = new_el("music", mei)

    facsimile = new_el("facsimile", music)
    surface = new_el("surface", facsimile)

    body = new_el("body", music)
    mdiv = new_el("mdiv", body)
    score = new_el("score", mdiv)
    scoreDef = new_el("scoreDef", score)
    staffGrp = new_el("staffGrp", scoreDef)
    staffDef = new_el("staffDef", staffGrp)

    staffDef.set("n", "1")
    staffDef.set("lines", "4")
    staffDef.set('notationtype', 'neume')
    staffDef.set('clef.line', '3')
    staffDef.set('clef.shape', 'C') 

    section = new_el("section", score)
    staff = new_el("staff", section)
    layer = new_el("layer", staff)

    # placeholder meiHead
    # title.setValue('MEI Encoding Output (%s)' % __version__)
   
    meiDoc = ET.ElementTree(mei)

    return meiDoc, surface, layer


def add_attributes_to_element(el, add):
    '''
    A helper function that takes in a dictionary linking attributes --> values, and adds all these
    attributes to the libMEI object @add.
    '''
    for key in add.keys():
        if add[key] == 'None':
            continue
        el.set(key, str(add[key]))
    return el


def create_primitive_element(xml, glyph, idx, surface):
    '''
    Creates a "lowest-level" element out of the xml retrieved from the MEI mapping tool (passed as
    an ElementTree object in @xml) and registers its bounding box in the given surface.
    '''
    res = new_el(xml.tag)
    attribs = xml.attrib #gets the attributes of them 

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
    res.set('facs', '#' + zoneId)
    
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

    parent = new_el(xml.tag)
    parent.extend(els) #append sequence of subelements (https://docs.python.org/3.8/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.extend)

    if len(els) < 2:
        return parent

    # if there's more than one element, must resolve intervals between ncs
    for i in range(1, len(els)):
        prev_nc = parent[i - 1]
        cur_nc = parent[i]
        new_pname, new_octave = resolve_interval(prev_nc, cur_nc)
        cur_nc.set('pname', new_pname)
        cur_nc.set('oct', new_octave)

        cur_nc.attrib.pop('intm',None) #remove attribute by popping it from the attrib list
    
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

    interval = cur_nc.get('intm')
    try:
        interval = interval.lower().replace('s', '')
        interval = int(interval)
    except ValueError:
        interval = 0
    except AttributeError:
        interval = 0

    starting_pitch = prev_nc.get('pname')
    starting_octave = int(prev_nc.get('oct'))
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
    el = new_el("zone", surface)
    # could be cleaner, but necessary so that we don't add extra attributes from @bb
    attribs = {
        'ulx': math.trunc(bb['ulx']),
        'uly': math.trunc(bb['uly']),
        'lrx': math.trunc(bb['lrx']),
        'lry': math.trunc(bb['lry']),
    }

    el = add_attributes_to_element(el, attribs)
    return el.get('xml:id')

def add_to_layer(syllable_dict, tag, layer, cur_syllable): 
    if ((syllable_dict["added"] is False) and (tag == "neume")):
        layer.append(cur_syllable)
        syllable_dict["added"] = True

def precedes_follows(syl_dict, layer, new_element):
    prev_syllable = syl_dict['opening_syl']
    new_syllable = new_el("syllable", layer)
    prev_syllable.set("xml:precedes", new_syllable.get('xml:id'))
    new_syllable.set("xml:follows", prev_syllable.get('xml:id'))
    syl_dict['opening_syl'] = new_syllable  #to be able to access most recent syllable 

    new_syllable.append(new_element)  #add new element to new syllable
    return new_syllable

def add_to_syllable(syl_dict, tag, layer, new_element, cur_syllable): 
    #To ensure that divLines are not leftmost element 
    #clefs and custos should be outside of the syllable 
    if ((tag != "neume") and ((syl_dict["neume_added"] == False) | (tag != "divLine"))): 
        layer.append(new_element)                    

    else: #divline or neume 
        #continue as normal (append to current syllable) 
        if ((syl_dict["latest"].tag == "divLine") | (syl_dict["latest"].tag == "neume")): 
            cur_syllable.append(new_element)                            
            add_to_layer(syl_dict, tag, layer, cur_syllable)
                                
        #if the last element was added outside of the current syllable 
        else: 
            #need to create a new syllable and add according precedes and follows attributes 
            if (syl_dict["added"] is True):  #syl, neume now precedes follows 
                
                cur_syllable = precedes_follows(syl_dict, layer, new_element) #update current syllable
            #if the syllable hasn't been added yet (no neume so far) then add new element to current syllable
            else : 
                cur_syllable.append(new_element)
                add_to_layer(syl_dict, tag, layer, cur_syllable)

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


    surface.set('lry', str(math.trunc(surface_bb['lry'])))
    surface.set('lrx', str(math.trunc(surface_bb['lrx'])))
    surface.set('ulx', str(math.trunc(surface_bb['ulx'])))
    surface.set('uly', str(math.trunc(surface_bb['uly'])))


    #add an initial system beginning
    sb = new_el("sb")
    bb = staves[0]['bounding_box']
    bb = {
        'ulx': bb['ulx'],
        'uly': bb['uly'],
        'lrx': bb['ulx'] + bb['ncols'],
        'lry': bb['uly'] + bb['nrows'],
    }
    zoneId = generate_zone(surface, bb)
    sb.set('facs', '#' + zoneId)
    layer.append(sb)

    # add to the MEI document, syllable by syllable
    for gs, syl_box in pairs:
        # print (gs)
        # print ("  ")
        # first add information about the text itself
        cur_syllable = new_el("syllable")
        bb = {
            'ulx': syl_box['ul'][0],
            'uly': syl_box['ul'][1],
            'lrx': syl_box['lr'][0],
            'lry': syl_box['lr'][1],
        }
        zoneId = generate_zone(surface, bb)

        # add syl element containing text on page
        syl = new_el("syl", cur_syllable)
        syl.text =  syl_box['syl']
        syl.set('facs', '#' + zoneId)

        syl_dict = {"opening_syl": cur_syllable, "latest": syl, "added": False, "neume_added": False}
        # iterate over glyphs on the page that fall within the bounds of this syllable
        for i, glyph in enumerate(gs):
            

            # are we done with neume components in this grouping?
            syllable_over = not any(('neume' in x['name']) for x in gs[i:])
            new_element = glyph_to_element(classifier, width_container, glyph, surface)
            
            if new_element is None:
                continue
            # four cases to consider:
            # 1. no line break and done with this syllable (everything gets added to layer)
            # 2. no line break and not done with this syllable
                # Case a: no neume has been added yet and new element is not neume (added to layer)
                # Case b: custos, clef, accid (added to layer)
                # Case c: neume or divline to be added, latest element was added inside the syllable 
                # Case d: neume or divline to be added, latest element was added outside the syllable, syllable has been
                #         added to the mei file (precedes and follows)
                # Case e: neume or divline to be added, latest element was added outside the syllable, syllable has not been 
                #         added to the mei file (add element to syllable & add syllable to file if new element is neume)
            # 3. a line break and done with this syllable (everything gets added to layer)
            # 4. a line break and not done with this syllable 
                # Same cases a to e (with added line break) 
            
            tag = new_element.tag 
        
            if not glyph['system_begin']:

                # case 1
                if syllable_over:
                    layer.append(new_element)
                    if (syl_dict["added"] is False):
                        layer.append(cur_syllable)
                        syl_dict["added"] = True

                # case 2
                else:
                    #need to handle all five cases, done with add_to_syllable
                    add_to_syllable(syl_dict, tag, layer, new_element, cur_syllable)

                    #need to update latest elemetn
                    syl_dict["latest"] = new_element 

                continue

            cur_staff = int(glyph['staff'])

            bb = staves[cur_staff]['bounding_box']
            bb = {
                'ulx': bb['ulx'],
                'uly': bb['uly'],
                'lrx': bb['ulx'] + bb['ncols'],
                'lry': bb['uly'] + bb['nrows'],
            }
            zoneId = generate_zone(surface, bb)  
            
            sb = new_el('sb')
            sb.set('facs', '#' + zoneId)   

            # case 3: the syllable is over, so the custos goes outside the syllable
            # do not include custos in <sb> tags! this was a typo in the MEI documentation
            if syllable_over:
                layer.append(new_element)
                layer.append(sb)
            # case 4 
            # syllable not over, so need to handle all five cases, done with add_to_syllable
            else:
                add_to_syllable(syl_dict, tag, layer, new_element, cur_syllable)

                #system break must be added to the layer 
                layer.append(sb)
                syl_dict["latest"] = sb

    return meiDoc

def merge_nearby_neume_components(meiDoc, width_mult):
    '''
    A heuristic to merge together neume components that are 1) consecutive 2) within the same
    syllable 3) within a certain distance from each other. This distance is by default set to the
    average width of a neume component within this page, but can be modified using the
    @width_multiplier argument. The output MEI will still be correct even if this method is not run.
    '''
    all_syllables = (meiDoc.getroot()).iter("syllable")
    allSurfaces = list((meiDoc.getroot()).iter('surface')) 
    surface = allSurfaces[0]  #only one surface so this gets it's corresponding element 
    
    surf_dict = {}
    neume_widths = []
    
    sc = list(surface) #gets all immediate children 
    for c in sc:
        surf_dict[c.get('xml:id')] = {}  #double check the id stuff
        for coord in c.attrib:
            if coord != "xml:id":
                coord_val = int(c.get(coord)) 
                surf_dict[c.get('xml:id')][coord] = coord_val

    neume_widths = [x['lrx'] - x['ulx'] for x in surf_dict.values()]
    med_neume_width = np.median(neume_widths) * width_mult
    # returns True if both inputs are of type 'neume' and they are close enough to be merged
    def compare_neumes(nl, nr):
        if not (nl.tag == 'neume' and nr.tag == 'neume'):
            return False
        nl_right_bound = max([surf_dict[n.get('facs')[1:]]['lrx'] for n in list(nl)])
        nr_left_bound = min([surf_dict[n.get('facs')[1:]]['ulx'] for n in list(nr)])

        distance = nr_left_bound - nl_right_bound  #ask tim about getting negative distances
        return (distance <= med_neume_width)

    for syllable in all_syllables:
        children = list(syllable) # need to only get all the direct children! 
        
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
                if target is None:
                    target = children[i]
            else:
                ncs_to_merge = []
                for neume in accumulator:           # empty contents of accumulator into ncs_to_merge
                    ncs_to_merge += list(neume)
                for nc in ncs_to_merge:             # merge all neume components 
                    target.append(nc)
                children_to_remove += accumulator
                target = None
                accumulator = []

        for neume in children_to_remove:
            syllable.remove(neume)

    return meiDoc

def removeEmptySyl(meiDoc): 
    '''
    Removes all empty syllables from the layer 
    '''

    layers = list((meiDoc.getroot()).iter('layer')) 
    layer = layers[0] #only one layer so this gets the corresponding element  

    #this could be cleaner
    for i in list(layer): 
        if (i.tag == "syllable"): 
            if (len(list(i)) == 1):
                if (list(i)[0].tag == "syl") & ((i.get("xml:precedes") is None) & (i.get("xml:follows") is None)) : 
                    layer.remove(i)

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

    meiDoc = removeEmptySyl(meiDoc)

    tree = ET.ElementTree(meiDoc.getroot())
    
    return ET.tostring(tree.getroot(),encoding='utf8').decode('utf8')


if __name__ == '__main__':

    # A script for running the encoding process locally on the salzinnes manuscript.
    # Replace paths and filenames as per your local setup.
    # Assumes that all files are numbered with the "CF-" filenames that the images of the manuscript
    # originally came with.

    classifier_fname = './tests/resources/square_notation_basic_classifier.csv'
    classifier, width_container = pct.fetch_table_from_csv(classifier_fname)

    f_inds = range(0, 200)

    for f_ind in f_inds:
        fname = 'salzinnes_{:0>3}'.format(f_ind)
        inJSOMR = './tests/resources/112rPF.json'
        in_syls = './tests/resources/112r.json'
        #in_png = '/Users/tim/Desktop/PNG_compressed/CF-{:0>3}.png'.format(f_ind)
        #out_fname = './out_mei/output_split_{}.mei'.format(fname)
        #out_fname_png = './out_png/{}_alignment.png'.format(fname)

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
        meiDoc = merge_nearby_neume_components(meiDoc, width_mult=0.55)
    print('remove empty syllables.... ')
    meiDoc = removeEmptySyl(meiDoc)

    tree = meiDoc
    tree.write("112r2-new.mei", encoding="utf-8")
