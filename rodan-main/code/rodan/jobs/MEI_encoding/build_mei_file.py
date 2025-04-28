# -*- coding: utf-8 -*-
from hashlib import new
from typing import List, Optional, Tuple, cast
from uuid import uuid4
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import (
    Element,
    SubElement,
    Comment,
    tostring,
)  # more concise?
import math
import numpy as np
import json
from rodan.jobs.MEI_encoding import parse_classifier_table as pct  # for rodan

# import parse_classifier_table as pct #---> for testing locally
from itertools import groupby
from rodan.jobs.MEI_encoding.state_machine import SylMachine

# from state_machine import SylMachine #---> for testing locally

try:
    from rodan.jobs.MEI_encoding import __version__
except ImportError:
    __version__ = "[Not encoded using Rodan]"


def new_el(name: str, p: Optional[Element] = None):
    """
    Create a new ElementTree Element with the given name and generate uuid4, with prefix 'm-'
    to conform with previous version
    """
    if p is None:
        element = ET.Element(name)
        element.set("xml:id", "m-" + str(uuid4()))
        return element
    else:
        element = ET.SubElement(p, name)
        element.set("xml:id", "m-" + str(uuid4()))
        return element


def add_flags_to_glyphs(glyphs: List[dict]):
    """
    Given the raw list of glyphs from pitch-finding containing position and classification
    information, add some information to the data structure. This lets us tell more easily where
    line breaks are in the file without having to re-perform calculations.
    """

    for g in glyphs:
        for key in g["glyph"].keys():
            g[key] = g["glyph"][key]
        for key in g["pitch"].keys():
            g[key] = g["pitch"][key]
        del g["pitch"]
        del g["glyph"]
        g["bounding_box"]["lrx"] = g["bounding_box"]["ulx"] + g["bounding_box"]["ncols"]
        g["bounding_box"]["lry"] = g["bounding_box"]["uly"] + g["bounding_box"]["nrows"]
        g["staff"] = int(g["staff"]) - 1

    # sort glyphs in lexicographical order by staff #, left to right
    glyphs.sort(key=lambda x: (int(x["staff"]), int(x["offset"])))

    for i in range(len(glyphs) - 1):
        temp1 = glyphs[i]
        temp2 = glyphs[i + 1]
        midpoint = (temp1["bounding_box"]["lrx"] + temp1["bounding_box"]["ulx"]) / 2
        if (
            temp2["bounding_box"]["ulx"] < midpoint
            and temp2["bounding_box"]["ulx"] >= temp1["bounding_box"]["ulx"]
        ):
            if temp1["bounding_box"]["uly"] < temp2["bounding_box"]["uly"]:
                glyphs[i + 1], glyphs[i] = temp1, temp2

    # add flag to every glyph denoting whether or not a line break should come immediately after
    for i in range(len(glyphs)):
        glyphs[i]["system_begin"] = False
        if i < len(glyphs) - 1:
            left_staff = int(glyphs[i]["staff"])
            right_staff = int(glyphs[i + 1]["staff"])

            if left_staff < right_staff:
                glyphs[i]["system_begin"] = True

    return glyphs


def neume_to_lyric_alignment(
    glyphs: List[dict], syl_boxes: List[dict], median_line_spacing: float
):
    """
    Given the processed glyphs from add_flags_to_glyphs and the information from the text alignment
    job (syl_boxes, median_line_spacing), finds out which syllables of text correspond to which
    glyphs on the page and returns a list of ([neumes], syllable) pairs.

    Things like custos, clefs, and accidentals are included inside these lists even though they
    are, strictly speaking, not part of the MEI for the syllable; that is handled in the method that
    actually encodes the MEI.
    """

    # if there's no syl information then make fake syllables for testing. this method makes one
    # large syllable covering an entire staff line.
    if not syl_boxes:
        glyphs = sorted(glyphs, key=lambda x: int(x["staff"]))

        grouped_glyphs = [
            list(g) for k, g in groupby(glyphs, key=lambda x: int(x["staff"]))
        ]
        dummy_syl = {"syl": "", "ul": [0, 0], "lr": [0, 0]}

        pairs = [(g, dummy_syl) for g in grouped_glyphs]
        return pairs

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
            g
            for g in glyphs[last_used:]
            if (
                box["ul"][1] - median_line_spacing
                < g["bounding_box"]["uly"]
                < box["ul"][1]
            )
            and (
                box["ul"][0]
                < g["bounding_box"]["ulx"] + g["bounding_box"]["ncols"] // 2
            )
        ]

        if not above_glyphs:
            starts.append(last_used)
            continue

        # find the glyph in above_glyphs that is closest to the current box
        nearest_glyph = min(above_glyphs, key=lambda g: g["bounding_box"]["ulx"])

        # append the index of this glyph to the start positions list
        starts.append(glyphs.index(nearest_glyph))
        last_used = max(starts)

    # if there are unassigned "orphan" glyphs at the beginning of the page,
    # force them to be assigned to the first syllable
    starts[0] = 0

    starts.append(len(glyphs))
    for i in range(len(starts) - 1):
        # it's possible that no glyphs are assigned to a syllable: in this case, just
        # get rid of the syllable altogether.
        glyph_range = glyphs[starts[i] : starts[i + 1]]
        if not glyph_range:
            continue

        pair = (glyph_range, syl_boxes[i])
        pairs.append(pair)

    return pairs


def generate_base_document(column_split_info: Optional[dict]):
    """
    Generates a generic template for an MEI document for neume notation.

    Currently a bit of this is hardcoded and should probably be made more customizable.
    """
    # create document (eventually going to need to link a bunch of documents together
    # under mei)

    mei = new_el("mei")
    mei.set("xmlns", "http://www.music-encoding.org/ns/mei")
    mei.set("meiversion", "5.1")

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

    # if multi column, add the colLayout tag to the score tag
    if column_split_info is not None:
        col_layout = new_el("colLayout", score)
        col_layout.set("cols", str(len(column_split_info["split_ranges"])))

    staffGrp = new_el("staffGrp", scoreDef)
    staffDef = new_el("staffDef", staffGrp)

    staffDef.set("n", "1")
    staffDef.set("lines", "4")
    staffDef.set("notationtype", "neume")
    staffDef.set("clef.line", "4")
    staffDef.set("clef.shape", "C")

    section = new_el("section", score)
    staff = new_el("staff", section)

    layer = new_el("layer", staff)

    # placeholder meiHead
    # title.setValue('MEI Encoding Output (%s)' % __version__)

    meiDoc = ET.ElementTree(mei)

    return meiDoc, surface, layer


def add_attributes_to_element(el: Element, add: dict):
    """
    A helper function that takes in a dictionary linking attributes --> values, and adds all these
    attributes to the libMEI object @add.
    """
    for key in add.keys():
        if add[key] == "None":
            continue
        el.set(key, str(add[key]))
    return el


def create_primitive_element(xml: Element, glyph: dict, idx: int, surface: Element):
    """
    Creates a "lowest-level" element out of the xml retrieved from the MEI mapping tool (passed as
    an ElementTree object in @xml) and registers its bounding box in the given surface.
    """
    res = new_el(xml.tag)
    attribs = xml.attrib  # gets the attributes of them

    # ncs, custos do not have a @line attribute. this is a bit of a hack...
    if xml.tag == "clef":
        attribs["line"] = str(int(float(glyph["strt_pos"])))

    attribs["oct"] = str(glyph["octave"])
    attribs["pname"] = str(glyph["note"])
    res = add_attributes_to_element(res, attribs)

    if type(glyph["bounding_box"]) == dict:
        zoneId = generate_zone(surface, glyph["bounding_box"])
    else:
        zoneId = generate_zone(surface, glyph["bounding_box"][idx])
    res.set("facs", "#" + zoneId)

    return res


def glyph_to_element(
    classifier: dict, width_container: dict, glyph: dict, surface: Element
):
    """
    Translates a glyph as output by the pitchfinder into an MEI element, registering bounding boxes
    in the given surface.

    Currently the assumption is that no MEI information in the given classifier is more than one
    level deep - that is, everything is either a single element (clef, custos) or the child of a
    single element (neumes). THIS IS NOT TRUE FOR ALL NEUMATIC NOTATION TYPES!

    UPDATE 2025.02: the given classifier can have 2 levels of depth, to handle cases like liquescent.
    TODO: consider to convert to recursive function to handle arbitrary depth.
    """
    name = str(glyph["name"])
    try:
        xml = classifier[name]
        width = width_container[name]
    except KeyError:
        print("entry {} not found in classifier table!".format(name))
        return None

    # remove everything up to the first dot in the name of the glyph
    try:
        name = name[: name.index(".")]
    except ValueError:
        pass

    # if this is an element with no children, then just apply a pitch and position to it
    if not list(xml):
        return create_primitive_element(xml, glyph, 0, surface)

    # else, this element has at least one child (is a neume)
    ncs = list(xml)

    # divide bbox according to the width column
    bb_org = glyph["bounding_box"]
    bb_new = []
    length_org = bb_org["lrx"] - bb_org["ulx"]
    length_nc = length_org / len(width)
    # iterate the list
    for i in range(len(width)):
        # count down the element
        for j in range(width[i]):
            bb_temp = {
                "ulx": bb_org["ulx"] + i * length_nc,
                "uly": bb_org["uly"],
                "lrx": bb_org["lrx"] + (i + 1) * length_nc,
                "lry": bb_org["uly"],
            }
            bb_new.append(bb_temp)
    glyph["bounding_box"] = bb_new

    els = []
    # els = [create_primitive_element(nc, glyph, surface) for nc in ncs]
    for i in range(len(ncs)):
        try:
            el = create_primitive_element(ncs[i], glyph, i, surface)
            if list(ncs[i]):
                for child in ncs[i]:
                    child_el = new_el(child.tag)
                    el.append(child_el)
        except IndexError:
            print(
                "Width column indicates {} neume components but gets {} neume components from input for classifier {}".format(
                    len(glyph["bounding_box"]), len(ncs), str(glyph["name"])
                )
            )
            continue
        els.append(el)

    parent = new_el(xml.tag)
    parent.extend(
        els
    )  # append sequence of subelements (https://docs.python.org/3.8/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.extend)

    if len(els) < 2:
        return parent

    # if there's more than one element, must resolve intervals between ncs
    for i in range(1, len(els)):
        prev_nc = parent[i - 1]
        cur_nc = parent[i]
        new_pname, new_octave = resolve_interval(prev_nc, cur_nc)
        cur_nc.set("pname", new_pname)
        cur_nc.set("oct", new_octave)

        cur_nc.attrib.pop(
            "intm", None
        )  # remove attribute by popping it from the attrib list

    return parent


def resolve_interval(prev_nc: Element, cur_nc: Element):
    """
    When given a ligature or something like that which specifies only the starting pitch and an
    interval, we need to calculate what the pitch of the rest of the notes are going to be. Given
    two neume components, where the second one has an 'intm' attribute, this calculates what the
    correct scale degree and octave is.

    N.B. in MEI octave numbers increase when going from a B to a C.
    """

    scale = ["c", "d", "e", "f", "g", "a", "b"]

    interval_attribute = cur_nc.get("intm")
    interval = 0
    if interval_attribute is not None:
        parsed = interval_attribute.lower().replace("s", "")
        try:
            interval = int(parsed)
        except ValueError:
            pass

    starting_pitch = prev_nc.get("pname")
    if starting_pitch is None:
        raise ValueError("pname attribute is None")

    octave_attribute = prev_nc.get("oct")
    if octave_attribute is None:
        raise ValueError("octave attribute is None")
    starting_octave = int(octave_attribute)
    end_octave = starting_octave

    try:
        start_index = scale.index(starting_pitch)
    except ValueError:
        raise ValueError("pname {} is not in scale {}".format(starting_pitch, scale))

    end_idx = start_index + interval

    if end_idx >= len(scale):
        end_octave += 1
    elif end_idx < 0:
        end_octave -= 1

    end_idx %= len(scale)
    end_pname = scale[end_idx]

    return str(end_pname), str(end_octave)


def generate_zone(surface: Element, bb: dict):
    """
    Given a bounding box, generates a zone element, adds it to the given @surface,
    and returns its ID.
    """
    el = new_el("zone", surface)
    # could be cleaner, but necessary so that we don't add extra attributes from @bb
    attribs = {
        "ulx": math.trunc(bb["ulx"]),
        "uly": math.trunc(bb["uly"]),
        "lrx": math.trunc(bb["lrx"]),
        "lry": math.trunc(bb["lry"]),
    }

    el = add_attributes_to_element(el, attribs)
    return cast(
        str, el.get("xml:id")
    )  # cast to str from Optional[str] as we know that xml:id will be present


def index_of_next_glyph_of_type(all_glyphs, glyph_type, starting_index=0):
    """
    Given a glyph and a list of glyphs, returns the index and glyph of the next glyph of glyph_type as a tuple (index, glyph).
    Returns None is there are no glyphs after starting_index with type glyph_type.
        @all_glyphs: A list of all glyphs in the document in sequence.
        @glyph_type: The type of the glyph we are looking for.
        @starting_index: The index in all_glyphs to start looking from.
    """
    return next(
        (
            index
            for index, glyph in enumerate(all_glyphs)
            if index >= starting_index and glyph_type in glyph["name"]
        ),
        None,
    )


def flatten_list(list):
    """
    Flattens a list of lists.
        @list: The list to be flattened.
    """
    return [item for sublist in list for item in sublist]


def get_custos_pitch_heuristic(all_glyphs, custos_glyph, max_distance_to_next_clef=5):
    """
    Given a custos glyph, tries to determine what it's pitch should be based on subsequent glyphs. Returns the pitch as a tuple (note, octave).
    This is a very naive implementation: We look for a clef glyph within max_distance_to_next_clef glyphs, then look for the next neume glyph after that.
    If we find both, it returns the pitch of the neume glyph. Otherwise, it returns the original pitch.
        @all_glyphs: A list of all glyphs in the document in sequence.
        @custos_glyph: The custos glyph.
        @max_distance_to_next_clef: The maximum distance to look for a clef glyph after the custos glyph.
    """

    current_pitch = (custos_glyph["note"], custos_glyph["octave"])
    custos_index = all_glyphs.index(custos_glyph)

    next_clef_index = index_of_next_glyph_of_type(all_glyphs, "clef", custos_index + 1)
    if (
        next_clef_index is None
        or next_clef_index - custos_index > max_distance_to_next_clef
    ):
        return current_pitch

    next_neume_index = index_of_next_glyph_of_type(
        all_glyphs, "neume", next_clef_index + 1
    )

    if next_neume_index is None:
        return current_pitch

    next_neume_glyph = all_glyphs[next_neume_index]
    return (next_neume_glyph["note"], next_neume_glyph["octave"])


def staff_to_columns_dict(staves: List[dict], height: int, num_columns):
    out = {}
    column = 0
    for i, staff in enumerate(staves):
        if staff["bounding_box"]["uly"] > (column + 1) * height:
            column += 1
        if column == num_columns:
            column = num_columns - 1
        out[i] = column
    return out


def column_bboxes(staff_to_column, system_boxes):
    out = []
    for i, box in enumerate(system_boxes):
        column = staff_to_column[i]
        if column >= len(out):
            out.append(box)
        else:
            out[column] = union_bbox(out[column], box)
    return out


def reformat_box(box: dict):
    bb = {
        "ulx": box["ulx"],
        "uly": box["uly"],
        "lrx": box["ulx"] + box["ncols"],
        "lry": box["uly"] + box["nrows"],
    }
    return bb


def union_bbox(box1: dict, box2: dict):
    """
    Returns the union of two bounding boxes.
    """
    if box1 is None:
        return box2
    return {
        "ulx": min(box1["ulx"], box2["ulx"]),
        "uly": min(box1["uly"], box2["uly"]),
        "lrx": max(box1["lrx"], box2["lrx"]),
        "lry": max(box1["lry"], box2["lry"]),
    }


def precompute_multi_column(
    glyphs: List[dict], column_split_info: dict, staves: List[dict]
):
    """
    Precomputes the column split information for multi column documents.
        @glyphs: A list of all glyphs in the document in sequence.
        @column_split_info: The column split information from the pitch finding JSON.
    """
    height = column_split_info["height"]
    prev_column = 0
    for glyph in glyphs:
        curr_column = column_split_info["staff_to_column"][int(glyph["staff"])]
        glyph["bounding_box"] = translate_bbox(
            glyph["bounding_box"],
            column_split_info["split_ranges"],
            height,
            curr_column,
        )
        glyph["column"] = curr_column
        if glyph["system_begin"] and curr_column > prev_column:
            glyph["column_begin"] = True
            prev_column = curr_column
        else:
            glyph["column_begin"] = False

    # translate staves
    for i, staff in enumerate(staves):
        curr_column = column_split_info["staff_to_column"][i]
        staff["bounding_box"] = translate_bbox(
            staff["bounding_box"],
            column_split_info["split_ranges"],
            height,
            curr_column,
        )

    return glyphs


def build_mei(
    pairs: List[Tuple[List[dict], dict]],
    classifier: dict,
    width_container: dict,
    staves: List[dict],
    page: dict,
    column_split_info: Optional[dict],
):
    """
    Encodes the final MEI document using:
        @pairs: Pairs from the neume_to_lyric_alignment.
        @classifier: The MEI mapping dictionary output
            by fetch_table_from_csv() in parse_classifier_table.py
        @width_container: The width column by fetch_table_from_csv() in parse_classifier_table.py
            the length of the list indicates the width of the neume,
            the sum of the list indicates the number of the ncs in the neume
        @staves: Bounding box information from pitch finding JSON.
        @page: Page dimension information from pitch finding JSON.
    """
    meiDoc, surface, layer = generate_base_document(column_split_info)

    # set the bounds of the page. If this is multi column then this will be overwritten
    surface_bb = {
        "ulx": page["bounding_box"]["ulx"],
        "uly": page["bounding_box"]["uly"],
        "lrx": page["bounding_box"]["ulx"] + page["bounding_box"]["ncols"],
        "lry": page["bounding_box"]["uly"] + page["bounding_box"]["nrows"],
    }

    # add pb element
    pb = new_el("pb")
    pb.set("n", "1")
    zoneId = surface.get("xml:id")
    pb.set("facs", "#" + zoneId)
    layer.append(pb)

    is_multi_column = column_split_info is not None

    # get a list of system bounding boxes that are formatted in ulx uly lrx lry format
    system_boxes = [staff["bounding_box"] for staff in staves]

    bb = system_boxes[0]

    if is_multi_column:
        # get height of original image, number of columns, and mapping for staves to columns
        height = column_split_info["height"]
        col_boxes = column_bboxes(column_split_info["staff_to_column"], system_boxes)

        # add initial column begin
        cb = new_el("cb")
        cb.set("n", "1")
        zoneId = generate_zone(surface, col_boxes[0])
        cb.set("facs", "#" + zoneId)
        layer.append(cb)

        # set the surface dimensions to match the original resized image
        surface_bb["lrx"] = column_split_info["width"]
        surface_bb["lry"] = column_split_info["height"]

    # set the dimensions of the page
    surface.set("lry", str(math.trunc(surface_bb["lry"])))
    surface.set("lrx", str(math.trunc(surface_bb["lrx"])))
    surface.set("ulx", str(math.trunc(surface_bb["ulx"])))
    surface.set("uly", str(math.trunc(surface_bb["uly"])))

    # add an initial system beginning
    sb = new_el("sb")

    zoneId = generate_zone(surface, bb)
    sb.set("facs", "#" + zoneId)
    sb.set("n", "1")
    layer.append(sb)

    # The flattened list of glyphs is used to search for the next neume after a custos.
    # we look forwards instead of storing the last custos because we simply updating an
    # element that has already been added to the layer doesn't work. We would have to find
    # it by id in the layer's children.
    all_glyphs = flatten_list([syllable_glyphs for syllable_glyphs, _ in pairs])

    # add to the MEI document, syllable by syllable
    for glyphs, syl_box in pairs:
        bb = {
            "ulx": syl_box["ul"][0],
            "uly": syl_box["ul"][1],
            "lrx": syl_box["lr"][0],
            "lry": syl_box["lr"][1],
        }

        # if there are multiple columns, shift the bounding box back accordingly
        if is_multi_column:
            col = bbox_to_col_num(bb, column_split_info["split_ranges"], height)
            bb = translate_bbox(bb, column_split_info["split_ranges"], height, col)

        # Pass both surface and layer
        machine = SylMachine(syl_box.get("syl", ""), bb, surface, layer)

        # find the last neume index
        last_neume_index = 0
        for i, g in enumerate(glyphs):
            if "neume" in g["name"]:
                last_neume_index = i

        # iterate over glyphs belonging to this syllable up to and including the final neume
        for i, glyph in enumerate(glyphs):
            # if this glyph is a custos, make it the same pitch as next neume
            if glyph["name"] == "custos":
                note, octave = get_custos_pitch_heuristic(all_glyphs, glyph)
                glyph["note"] = note
                glyph["octave"] = octave

            # new_element is of type ET.Element. <neueme>, <divLine>, <clef>, <accid>, <custos>, etc.
            new_element = glyph_to_element(classifier, width_container, glyph, surface)
            # TODO
            # Investigate why new_element can be None
            if new_element is None:
                continue
            # tag is "neume", "divLine", "clef", "accid", "custos", etc.
            tag = new_element.tag

            # the state machine is responsible for abstracting the confusing logic of when to add
            # an element inside vs outside the syllable. An optimization we make is that we find where the last
            # neume is, and consider that the true end of the syllable, and every glyph associated with this syllable
            # that comes after that are added outside the syllable.
            if i <= last_neume_index:
                machine.read(tag, new_element)
            else:
                machine.read_outside_syllable(new_element)

            if is_multi_column and glyph["column_begin"]:  # reached a column begin
                # start new cb
                cb = new_el("cb")
                cb.set("n", str(glyph["column"] + 1))
                zoneId = generate_zone(surface, col_boxes[glyph["column"]])
                cb.set("facs", "#" + zoneId)
                machine.read(cb.tag, cb)

            if glyph["system_begin"]:  # reached a system begin
                next_staff = int(glyph["staff"]) + 1
                bb = system_boxes[next_staff]
                # create a new system begin
                zoneId = generate_zone(surface, bb)
                sb = new_el("sb")
                sb.set("facs", "#" + zoneId)
                sb.set("n", str(next_staff + 1))
                machine.read(sb.tag, sb)

    return meiDoc


def merge_nearby_neume_components(meiDoc: ET.ElementTree, width_mult: float):
    """
    A heuristic to merge together neume components that are 1) consecutive 2) within the same
    syllable 3) within a certain distance from each other. This distance is by default set to the
    average width of a neume component within this page, but can be modified using the
    @width_multiplier argument. The output MEI will still be correct even if this method is not run.
    """
    all_syllables = (meiDoc.getroot()).iter("syllable")
    allSurfaces = list((meiDoc.getroot()).iter("surface"))
    surface = allSurfaces[0]  # only one surface so this gets it's corresponding element

    surf_dict: dict = {}
    neume_widths: list = []

    sc = list(surface)  # gets all immediate children
    for c in sc:
        surf_dict[c.get("xml:id")] = {}  # double check the id stuff
        for coord in c.attrib:
            if coord != "xml:id":
                coord_val = int(c.get(coord))
                surf_dict[c.get("xml:id")][coord] = coord_val

    neume_widths = [x["lrx"] - x["ulx"] for x in surf_dict.values()]
    med_neume_width = np.median(neume_widths) * width_mult

    # returns True if both inputs are of type 'neume' and they are close enough to be merged
    def compare_neumes(nl: Element, nr: Element):
        if not (nl.tag == "neume" and nr.tag == "neume"):
            return False
        nl_right_bound = max(
            [surf_dict[n.get("facs", "")[1:]]["lrx"] for n in list(nl)]
        )
        nr_left_bound = min([surf_dict[n.get("facs", "")[1:]]["ulx"] for n in list(nr)])

        distance = (
            nr_left_bound - nl_right_bound
        )  # ask tim about getting negative distances
        return distance <= med_neume_width

    for syllable in all_syllables:
        children = list(syllable)  # need to only get all the direct children!

        # holds children of the current syllable that will be added to target
        accumulator: List[Element] = []

        # holds the first neume in a sequence of neumes that will be merged
        target: Optional[Element] = None

        # holds children once in the accumulator that must be removed after iteration is done
        children_to_remove: List[Element] = []

        # iterate over all children. for each neume decide whether or not it should be merged
        # with the next one using compare_neumes. if yes, add the next one to the accumulator.
        # if not, empty the accumulator and add its contents to the target.

        for i in range(len(children)):
            if (i + 1 < len(children)) and (
                compare_neumes(children[i], children[i + 1])
            ):
                accumulator.append(children[i + 1])
                if target is None:
                    target = children[i]
            else:
                ncs_to_merge = []
                for (
                    neume
                ) in accumulator:  # empty contents of accumulator into ncs_to_merge
                    ncs_to_merge += list(neume)
                for nc in ncs_to_merge:  # merge all neume components
                    if target is not None:
                        target.append(nc)
                children_to_remove += accumulator
                target = None
                accumulator = []

        for neume in children_to_remove:
            syllable.remove(neume)

    return meiDoc


def reformat_staves(staves: List[dict]):
    """
    Reformats the bounding box information from the pitch finding JSON.
    """
    for staff in staves:
        staff["bounding_box"] = reformat_box(staff["bounding_box"])
    return staves


def process(
    jsomr: dict,
    syls: dict,
    classifier: dict,
    width_mult: float,
    width_container: dict,
    column_split_info: dict,
    verbose: bool = True,
):
    """
    Runs the entire MEI encoding process given the three inputs to the rodan job and the
    width_multiplier parameter for merging neume components.
    """
    staves = reformat_staves(jsomr["staves"])
    glyphs = jsomr["glyphs"]
    syl_boxes = syls["syl_boxes"] if syls is not None else None
    median_line_spacing = syls["median_line_spacing"] if syls is not None else None

    glyphs = add_flags_to_glyphs(glyphs)
    pairs = neume_to_lyric_alignment(glyphs, syl_boxes, median_line_spacing)
    if column_split_info is not None:
        staff_to_column = staff_to_columns_dict(
            staves, column_split_info["height"], len(column_split_info["split_ranges"])
        )
        column_split_info["staff_to_column"] = staff_to_column
        precompute_multi_column(glyphs, column_split_info, staves)
    meiDoc = build_mei(
        pairs, classifier, width_container, staves, jsomr["page"], column_split_info
    )

    if width_mult > 0:
        meiDoc = merge_nearby_neume_components(meiDoc, width_mult=width_mult)

    tree = ET.ElementTree(meiDoc.getroot())
    return ET.tostring(tree.getroot(), encoding="utf8").decode("utf8")


def bbox_to_col_num(bbox: dict, ranges: List, height: int):
    col = 0
    for i in range(len(ranges)):
        if bbox["uly"] <= (i + 1) * height:
            col = i
            break
    return col


def translate_bbox(bbox: dict, ranges: list, height: int, col: int):
    """
    When there are multiple columns, this function is used to reposition the bounding
    box of a syl to be where it belongs on the original page
    """

    ulx, uly, lrx, lry = bbox["ulx"], bbox["uly"], bbox["lrx"], bbox["lry"]
    new_uly = uly - height * col
    new_ulx = ulx + ranges[col][0]
    new_lry = lry - height * col
    new_lrx = lrx + ranges[col][0]
    new_box = {"ulx": new_ulx, "uly": new_uly, "lrx": new_lrx, "lry": new_lry}
    if "nrows" in bbox:
        new_box["nrows"] = bbox["nrows"]
    if "ncols" in bbox:
        new_box["ncols"] = bbox["ncols"]
    return new_box
