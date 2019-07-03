from pymei import XmlImport
from gamera.core import *
import os
init_gamera()
import pdb

from optparse import OptionParser

if __name__ == "__main__":
    usage = "usage: %prog [options] input_mei_file input_image_file output_folder"
    opts = OptionParser(usage)
    (options, args) = opts.parse_args()

    input_file = args[0]
    output_folder = args[2]
    mdoc = XmlImport.documentFromFile(input_file)

    neumes = mdoc.getElementsByName('neume')
    clefs = mdoc.getElementsByName('clef')
    divisions = mdoc.getElementsByName('division')
    custos = mdoc.getElementsByName('custos')
    systems = mdoc.getElementsByName('system')

    img = load_image(args[1])

    if img.pixel_type_name != "OneBit":
        img = img.to_onebit()

    rgb = Image(img, RGB)

    neumecolour = RGBPixel(255, 0, 0)
    clefcolour = RGBPixel(0, 255, 0)
    divisioncolour = RGBPixel(0, 0, 255)
    custoscolour = RGBPixel(128, 128, 0)
    systemscolour = RGBPixel(200, 200, 200)

    for system in systems:
        facs = system.getAttribute("facs").getValue()
        facs_el = mdoc.getElementById(facs)
        ulx = facs_el.getAttribute("ulx").getValue()
        uly = facs_el.getAttribute("uly").getValue()
        lrx = facs_el.getAttribute("lrx").getValue()
        lry = facs_el.getAttribute("lry").getValue()
        rgb.draw_filled_rect((int(ulx) - 5, int(uly) - 5), (int(lrx) + 5, int(lry) + 5), systemscolour)

    for neume in neumes:
        facs = neume.getAttribute("facs").getValue()
        facs_el = mdoc.getElementById(facs)
        ulx = facs_el.getAttribute("ulx").getValue()
        uly = facs_el.getAttribute("uly").getValue()
        lrx = facs_el.getAttribute("lrx").getValue()
        lry = facs_el.getAttribute("lry").getValue()
        rgb.draw_filled_rect((int(ulx) - 5, int(uly) - 5), (int(lrx) + 5, int(lry) + 5), neumecolour)

        note_string = '-'.join([note.getAttribute("pname").getValue() for note in neume.getDescendantsByName('note')])

        print(note_string)
        # rgb.draw_text((int(ulx) - 0, int(uly) - 20), note_string, RGBPixel(0,0,0), size=10, bold=True, halign="left")
        # rgb.draw_text((int(ulx) - 20, int(uly) - 50), neume.getAttribute('name').getValue(), RGBPixel(0,0,0), size=10, bold=True, halign="left")

    for clef in clefs:
        facs = clef.getAttribute("facs").getValue()
        facs_el = mdoc.getElementById(facs)
        ulx = facs_el.getAttribute("ulx").getValue()
        uly = facs_el.getAttribute("uly").getValue()
        lrx = facs_el.getAttribute("lrx").getValue()
        lry = facs_el.getAttribute("lry").getValue()
        rgb.draw_filled_rect((int(ulx) - 5, int(uly) - 5), (int(lrx) + 5, int(lry) + 5), clefcolour)

    # for division in divisions:
    #     facs = mdoc.get_by_facs(division.facs)[0]
    #     rgb.draw_filled_rect((int(facs.ulx) - 5, int(facs.uly) - 5), (int(facs.lrx) + 5, int(facs.lry) + 5), divisioncolour)

    # for custo in custos:
    #     facs = mdoc.get_by_facs(custo.facs)[0]
    #     rgb.draw_filled_rect((int(facs.ulx) - 5, int(facs.uly) - 5), (int(facs.lrx) + 5, int(facs.lry) + 5), custoscolour)

    rgb.highlight(img, RGBPixel(0, 0, 0))

    rgb.save_PNG(os.path.join(output_folder, 'pitch_find.png'))
