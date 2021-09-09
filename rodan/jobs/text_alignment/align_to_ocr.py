# -*- coding: utf-8 -*-
import os
import shutil
import numpy as np
import subprocess
import json
import re
from skimage import io

try:
    from . import affine_needleman_wunsch as afw
    from . import latin_syllabification as latsyl
    from . import perform_ocr
    from . import image_preprocessing as preproc
except (ImportError, SystemError):
    import affine_needleman_wunsch as afw
    import latin_syllabification as latsyl
    import perform_ocr
    import image_preprocessing as preproc


def read_file(fname):
    '''
    helper function for reading a plaintext transcript of a manuscript page
    '''
    file = open(fname, 'r')
    lines = file.readlines()
    file.close()
    lines = ' '.join(x for x in lines if not x[0] == '#')
    lines = lines.replace('\n', '')
    lines = lines.replace('\r', '')
    lines = lines.replace('| ', '')
    # lines = unidecode(lines)
    return lines


def rotate_bbox(cbox, angle, pivot, radians=False):
    px, py = pivot

    if not radians:
        angle = angle * np.pi / 180

    s = np.sin(angle)
    c = np.cos(angle)

    old_ulx = cbox.ulx
    old_uly = cbox.uly
    old_lrx = cbox.lrx
    old_lry = cbox.lry

    # rotate using a 2d rotation matrix
    new_ulx = (old_ulx * c) - (old_uly * s)
    new_uly = (old_ulx * s) + (old_uly * c)
    new_lrx = (old_lrx * c) - (old_lry * s)
    new_lry = (old_lrx * s) + (old_lry * c)

    new_ul = np.round([new_ulx, new_uly]).astype('int16')
    new_lr = np.round([new_lrx, new_lry]).astype('int16')

    return perform_ocr.CharBox(cbox.char, new_ul, new_lr)


def process(raw_image,
            transcript,
            ocr_model_name,
            seq_align_params={},
            existing_ocr=None,
            verbose=True):
    '''
    given a text layer image @raw_image and a string transcript @transcript, performs preprocessing
    and OCR on the text layer and then aligns the results to the transcript text.
    '''

    # -- PRE-PROCESSING --
    # get raw image of text layer and preform preprocessing to find text lines
    print('identifying text lines...')
    image, eroded, angle = preproc.preprocess_images(raw_image)
    cc_strips, lines_peak_locs, _ = preproc.identify_text_lines(eroded)

    # -- PERFORM OCR WITH CALAMARI --
    all_chars = existing_ocr
    if not all_chars:
        all_chars = perform_ocr.recognize_text_strips(image, cc_strips, ocr_model_name, verbose)
    all_chars = perform_ocr.handle_abbreviations(all_chars)

    # -- PERFORM AND PARSE ALIGNMENT --
    # get full ocr transcript as CharBoxes
    ocr = ''.join(x.char for x in all_chars)
    all_chars_copy = list(all_chars)

    # remove special characters, but maintain case
    transcript = latsyl.clean_transcript(transcript)

    # affine_needleman_wunsch alignment between OCR and transcript
    print('performing alignment...')
    tra_align, ocr_align, _ = afw.perform_alignment(
        transcript=list(transcript),
        ocr=list(ocr),
        **seq_align_params
        )
    tra_align = ''.join(tra_align)
    ocr_align = ''.join(ocr_align)

    # -- SPLIT INTO SYLLABLES --
    print('syllabifying...')
    syls = latsyl.syllabify_text(transcript)
    align_transcript_boxes = []
    current_offset = 0
    syl_boxes = []

    # -- MATCH SYLLABLES TO ALIGNED  --
    print('matching syllables to alignment...')
    # insert gaps into ocr output based on alignment string. this causes all_chars to have gaps at the
    # same points as the ocr_align string does, and is thus the same length as tra_align.
    for i, char in enumerate(ocr_align):
        if char == '_':
            all_chars.insert(i, perform_ocr.CharBox('_'))

    # this could very possibly go wrong (special chars, bug in alignment algorithm, etc) so better
    # make sure that this condition is holding at this point
    assert len(all_chars) == len(tra_align), 'all_chars not same length as alignment: ' \
        '{} vs {}'.format(len(all_chars), len(tra_align))

    # for each syllable in the transcript, find what characters (or gaps) of the ocr that syllable
    # is aligned to.
    for syl in syls:
        if len(syl) < 1:
            continue
        elif len(syl) == 1:
            syl_regex = syl
        else:
            syl_regex = syl[0] + syl[1:-1].replace('', '_*') + syl[-1]

        syl_match = re.search(syl_regex, tra_align[current_offset:], re.IGNORECASE)
        start = syl_match.start() + current_offset
        end = syl_match.end() + current_offset
        current_offset = end
        align_boxes = [x for x in all_chars[start:end] if x.lr is not None]

        # if align_boxes is empty then this syllable got aligned to nothing in the ocr. ignore it.
        if not align_boxes:
            continue

        # if align_boxes has boxes that lie on multiple text lines then we're trying to align this
        # single syllable over multiple lines. remove all boxes on the upper line.
        if len(set([x.uly for x in align_boxes])) > 1:
            lower_level = max(x.uly for x in align_boxes)
            align_boxes = [b for b in align_boxes if b.uly == lower_level]

        new_ul = (min(x.ulx for x in align_boxes), min(x.uly for x in align_boxes))
        new_lr = (max(x.lrx for x in align_boxes), max(x.lry for x in align_boxes))
        syl_boxes.append(perform_ocr.CharBox(syl, new_ul, new_lr))

    print('rotating bboxes again...')
    # finally, rotate syl_boxes back by the angle that the page was rotated by
    pivot = (image.shape[0] // 2, image.shape[1] // 2)
    for i in range(len(syl_boxes)):
        syl_boxes[i] = rotate_bbox(syl_boxes[i], angle, pivot)

    return syl_boxes, image, lines_peak_locs, all_chars_copy


def to_JSON_dict(syl_boxes, lines_peak_locs):
    '''
    turns the output of the process script into a JSON dict that can be passed into the MEI_encoding
    rodan job.
    '''
    med_line_spacing = np.quantile(np.diff(lines_peak_locs), 0.75)

    data = {}
    data['median_line_spacing'] = med_line_spacing
    data['syl_boxes'] = []

    for s in syl_boxes:
        data['syl_boxes'].append({
            'syl': s.char,
            'ul': [int(s.ul[0]), int(s.ul[1])],
            'lr': [int(s.lr[0]), int(s.lr[1])]
        })

    return data


def draw_results_on_page(image, syl_boxes, lines_peak_locs, out_fname):
    '''
    draws a list of char_boxes on a given image and saves the image to file (local dev use only).
    '''
    im = Image.fromarray(image)
    text_size = im.size[1] // 70
    fnt = ImageFont.truetype('FreeMono.ttf', text_size)
    draw = ImageDraw.Draw(im)

    for i, cbox in enumerate(syl_boxes):
        if cbox.char in '. ':
            continue

        ul = cbox.ul
        lr = cbox.lr
        draw.rectangle([ul[0], ul[1] - text_size, ul[0] + text_size * len(cbox.char) * 0.6, ul[1]], fill='white')
        draw.text((ul[0], ul[1] - text_size), cbox.char, font=fnt, fill='black')
        draw.rectangle([ul, lr], outline='black')
        draw.line([ul[0], ul[1], ul[0], lr[1]], fill='black', width=5)

    # for i, peak_loc in enumerate(lines_peak_locs):
    #     draw.text((1, peak_loc - text_size), 'line {}'.format(i), font=fnt, fill='gray')
    #     draw.line([0, peak_loc, im.width, peak_loc], fill='gray', width=3)

    im.save(out_fname)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import parse_cantus_csv as pcc
    import PIL
    import pickle
    from PIL import Image, ImageDraw, ImageFont
    import os

    text_func = pcc.filename_to_text_func('./csv/123723_Salzinnes.csv', './csv/mapping.csv')
    manuscript = 'salzinnes'
    f_inds = ['040r', '142v', '087r', '132v']
    ocr_model = 'salzinnes-gothic-2019'

    # text_func = pcc.filename_to_text_func('./csv/einsiedeln_123606.csv')
    # manuscript = 'einsiedeln'
    # f_inds = range(0, 11)
    # ocr_model = './salzinnes_model-00054500.pyrnn.gz'

    # text_func = pcc.filename_to_text_func('./csv/stgall390_123717.csv')
    # manuscript = 'stgall390'
    # f_inds = ['022', '023', '024', '025', '007']
    # ocr_model = 'stgall2-00017000.pyrnn.gz'

    # text_func = pcc.filename_to_text_func('./csv/stgall388_123750.csv')
    # manuscript = 'stgall388'
    # f_inds = ['028', '029', '030', '031', '032']
    # ocr_model = 'stgall3-00017000.pyrnn.gz'

    for ind in f_inds:

        try:
            f_id, transcript = text_func(ind)
        except ValueError as e:
            print(e)
            print('no chants listed for page {}'.format(ind))
            continue

        fname = '{}_{}'.format(manuscript, f_id)
        ocr_pickle = None 
        text_layer_fname = r'D:\Desktop\rodan resources\aligner\png\{}_text.png'.format(fname)

        if not os.path.isfile(text_layer_fname):
            print('cannot find files for {}.'.format(fname))
            continue

        print('processing {}...'.format(fname))
        raw_image = io.imread(text_layer_fname)

        existing_ocr = None

        result = process(raw_image, transcript, ocr_model, existing_ocr=existing_ocr, verbose=True)

        if result is None:
            continue
        syl_boxes, image, lines_peak_locs, all_chars = result
        with open(r'D:\Desktop\rodan resources\aligner\out_json\{}.json'.format(fname), 'w') as outjson:
            json.dump(to_JSON_dict(syl_boxes, lines_peak_locs), outjson)
        # with open('./pik/{}_boxes.pickle'.format(fname), 'wb') as f:
        #     pickle.dump(all_chars, f, -1)

        out_fname = r'D:\Desktop\rodan resources\aligner\out_imgs\aligned_{}.png'.format(fname)
        draw_results_on_page(raw_image, syl_boxes, lines_peak_locs, out_fname)
