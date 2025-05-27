import PIL
import pickle
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import json
import numpy as np
import textAlignPreprocessing as preproc
import os
import parse_cantus_csv as pcc
import textSeqCompare as tsc
import alignToOCR as atocr
from itertools import product
reload(atocr)


def intersect(bb1, bb2):
    '''
    takes two bounding boxes as an argument. if they overlap, return the area of the overlap;
    else, return False
    '''
    lr1 = bb1['lr']
    ul1 = bb1['ul']
    lr2 = bb2['lr']
    ul2 = bb2['ul']

    dx = min(lr1[0], lr2[0]) - max(ul1[0], ul2[0])
    dy = min(lr1[1], lr2[1]) - max(ul1[1], ul2[1])
    if (dx > 0) and (dy > 0):
        return dx*dy
    else:
        return False


def IOU(bb1, bb2):
    '''
    intersection over union between two bounding boxes
    '''
    lr1 = bb1['lr']
    ul1 = bb1['ul']
    lr2 = bb2['lr']
    ul2 = bb2['ul']

    # first find area of intersection:
    new_ulx = max(ul1[0], ul2[0])
    new_uly = max(ul1[1], ul2[1])
    new_lrx = min(lr1[0], lr2[0])
    new_lry = min(lr1[1], lr2[1])

    area_int = (new_lrx - new_ulx) * (new_lry - new_uly)
    area_1 = (lr1[0] - ul1[0]) * (lr1[1] - ul1[1])
    area_2 = (lr2[0] - ul2[0]) * (lr2[1] - ul2[1])

    return float(area_int) / (area_1 + area_2 - area_int)


def black_area_IOU(bb1, bb2, image):
    '''
    intersection over union between two bounding boxes
    '''
    lr1 = bb1['lr']
    ul1 = bb1['ul']
    lr2 = bb2['lr']
    ul2 = bb2['ul']

    new_ul = (max(ul1[0], ul2[0]), max(ul1[1], ul2[1]))
    new_lr = (min(lr1[0], lr2[0]), min(lr1[1], lr2[1]))

    bb1_subimage = image.subimage(ul1, lr1)
    bb2_subimage = image.subimage(ul2, lr2)
    intersect_subimage = image.subimage(new_ul, new_lr)

    bb1_black = bb1_subimage.black_area()[0]
    bb2_black = bb2_subimage.black_area()[0]
    intersect_black = intersect_subimage.black_area()[0]

    return float(intersect_black) / (bb1_black + bb2_black - intersect_black)


def evaluate_alignment(manuscript, ind, eval_difficult=False, json_dict=None):

    fname = '{}_{}'.format(manuscript, ind)
    gt_xml = ET.parse('./ground-truth-alignments/{}_gt.xml'.format(fname))
    gt_boxes = []
    els = list(gt_xml.getroot())
    for el in els:
        if not el.tag == 'object':
            continue
        diff = int(el.find('difficult').text)
        name = el.find('name').text
        bb = el.find('bndbox')
        ul = int(bb.find('xmin').text), int(bb.find('ymin').text)
        lr = int(bb.find('xmax').text), int(bb.find('ymax').text)
        gt_boxes.append({
            'syl': name,
            'difficult': diff,
            'ul': ul,
            'lr': lr
        })

    if json_dict:
        align_boxes = json_dict['syl_boxes']
    else:
        with open('./out_json/{}.json'.format(fname), 'r') as j:
            align_boxes = json.load(j)['syl_boxes']

    raw_image = gc.load_image('./png/' + fname + '_text.png')
    image, _, _ = preproc.preprocess_images(raw_image, correct_rotation=False)

    score = {}
    area_score = {}
    for box in gt_boxes:
        if box['difficult'] and not eval_difficult:
            continue
        same_syl_boxes = [x for x in align_boxes
            if x['syl'] in box['syl']
            or box['syl'] in x['syl']
            ]
        if not same_syl_boxes:
            score[box['syl']] = 0
            area_score[box['syl']] = 0
            continue
        ints = [intersect(box, x) for x in same_syl_boxes]
        if not any(ints):
            score[box['syl']] = 0
            area_score[box['syl']] = 0
            continue
        best_box = same_syl_boxes[ints.index(max(ints))]
        score[box['syl']] = IOU(box, best_box)
        area_score[box['syl']] = black_area_IOU(box, best_box, image)

    return (np.mean(score.values()), np.mean(area_score.values()))


def try_params(params):

    gts = [{
        'manuscript': 'salzinnes',
        'folio': '020v',
        'text_func': pcc.filename_to_text_func('./csv/123723_Salzinnes.csv', './csv/mapping.csv'),
        'ocr_model': './models/salzinnes_model-00054500.pyrnn.gz'
    }, {
        'manuscript': 'salzinnes',
        'folio': 25,
        'text_func': pcc.filename_to_text_func('./csv/123723_Salzinnes.csv', './csv/mapping.csv'),
        'ocr_model': './models/salzinnes_model-00054500.pyrnn.gz'
    }, {
        'manuscript': 'stgall390',
        'folio': '023',
        'text_func': pcc.filename_to_text_func('./csv/stgall390_123717.csv'),
        'ocr_model': './models/stgall2-00017000.pyrnn.gz'
    }]

    results = []
    for x in gts:
        f_ind, transcript = x['text_func'](x['folio'])
        manuscript = x['manuscript']
        fname = '{}_{}'.format(manuscript, f_ind)
        ocr_model = x['ocr_model']
        ocr_pickle = './pik/{}_boxes.pickle'.format(fname)
        text_layer_fname = './png/{}_text.png'.format(fname)
        raw_image = gc.load_image('./png/' + fname + '_text.png')

        result = atocr.process(raw_image, transcript,
            ocr_model, seq_align_params=params, existing_ocr_pickle=ocr_pickle)

        syl_boxes, image, lines_peak_locs, all_chars = result
        json_dict = atocr.to_JSON_dict(syl_boxes, lines_peak_locs)
        res = evaluate_alignment(manuscript, f_ind, eval_difficult=False, json_dict=json_dict)

        with open('./pik/{}_boxes.pickle'.format(fname), 'wb') as f:
            pickle.dump(all_chars, f, -1)

        results.append(res[1])

    return np.mean(results)


def test_ocropus_model(path, seq_align_params=[0, -1, -1, -1]):
    pairs = []
    # path = '/Users/tim/Documents/ocropy-training/all'
    path = '/Users/tim/Documents/ocropy-training/gall2'
    for dir, folders, files in os.walk(path):
        for file in files:
            if not file.split('.')[-2] == 'gt':
                continue
            with open('{}/{}'.format(dir, file)) as f:
                gt = f.read()
            ocr_fname = file.split('.')[0] + '.txt'
            with open('{}/{}'.format(dir, ocr_fname)) as f:
                ocr = f.read()
            pairs.append((gt, ocr))

    scores = []
    for gt, ocr in pairs:
        _, _, score = tsc.perform_alignment(list(gt), list(ocr), seq_align_params)
        scores.append(score)
    final_score = sum(scores) / sum(len(x[0]) for x in pairs)

    return final_score

if __name__ == '__main__':
    logs = {}

    params = np.array(list(product(
        [5, 8, 11],
        [-4, -7, -10],
        [-2, -5, -7],
        [-2, -5, -7],
        [0, -3, -5],
        [0, -3, -5],
    )))
    np.random.shuffle(params)

    for p in params:
        res = try_params(p)
        logs[tuple(p)] = res
        print(p, res)

    p = [(k, logs[tuple(k)]) for k in logs.keys()]
    p = sorted(p, key=lambda x: x[1])
    print(p)
