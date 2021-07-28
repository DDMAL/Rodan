import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pymei import MeiDocument, MeiElement, MeiAttribute, documentToText, documentToFile

# This file contains only functions for drawing out intermediate results of the alignment, for
# use when developing; nothing here is called in the rodan job.


def draw_neume_alignment(in_png, out_fname, pairs, text_size=60):
    '''
    Given the pairs from neume_to_lyric_alignment, draws the result on the original page (given a
    path to the .png)
    '''
    fnt = ImageFont.truetype('FreeMono.ttf', text_size)
    im = Image.open(in_png).convert('RGB')
    draw = ImageDraw.Draw(im)

    last_text = None
    for gs, tb in pairs:
        if not tb:
            continue

        draw.rectangle(tb['ul'] + tb['lr'], outline='black')
        # draw.text(tb['ul'], tb['syl'], font=fnt, fill='gray')
        for g in gs:

            if 'clef' in g['name'] or 'custos' in g['name']:
                continue

            bb = g['bounding_box']
            pt1 = (bb['ulx'] + bb['ncols'] // 2, bb['uly'] + bb['nrows'] // 2)
            pt2 = ((tb['ul'][0] + tb['lr'][0]) // 2, (tb['ul'][1] + tb['lr'][1]) // 2)

            if pt1[1] > pt2[1]:
                continue

            draw.line((pt1, pt2), fill='black', width=5)
    im.save(out_fname)


def draw_mei_doc(in_png, out_fname, meiDoc, text_size=60):
    '''
    Given an encoded mei_doc result, draws the result on the original page (given a
    path to the .png)
    '''

    fnt = ImageFont.truetype('FreeMono.ttf', text_size)
    im = Image.open(in_png).convert('RGB')
    draw = ImageDraw.Draw(im)

    all_syllables = meiDoc.getElementsByName('syllable')
    surface = meiDoc.getElementsByName('surface')[0]

    # build a dictionary linking each zone's ID to its element object for easy access
    surf_dict = {}
    for c in surface.getChildren():
        surf_dict[c.id] = {}
        for coord in c.attributes:
            surf_dict[c.id][coord.name] = int(coord.value)

    for syllable in all_syllables:
        neumes = syllable.getChildrenByName('neume')

        for n in neumes:
            nc_ids = [x.getAttribute('facs').value[1:] for x in n.children]
            zones = [surf_dict[x] for x in nc_ids]
            ulx = min([z['ulx'] for z in zones])
            uly = min([z['uly'] for z in zones])
            lrx = max([z['lrx'] for z in zones])
            lry = max([z['lry'] for z in zones])

            draw.rectangle((ulx, uly, lrx, lry), outline='black')
            neume_avg_x = (ulx + lrx) // 2
            neume_avg_y = (uly + lry) // 2

            syl = syllable.getChildrenByName('syl')[0]
            syl_zone = surf_dict[syl.getAttribute('facs').value[1:]]
            syl_avg_x = (syl_zone['ulx'] + syl_zone['lrx']) // 2
            syl_avg_y = (syl_zone['uly'] + syl_zone['lry']) // 2

            # don't draw a line to a blank syllable
            if not syl_avg_x or syl_avg_y:
                continue
            draw.line((neume_avg_x, neume_avg_y, syl_avg_x, syl_avg_y), fill='black', width=3)

    im.save(out_fname)
