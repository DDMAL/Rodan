# -*- coding: utf-8 -*-
try:
    from calamari_ocr.ocr.predictor import Predictor
except ImportError:
    print('Calamari OCR failed to import. This is normal only when loading Rodan.')
import os


abbreviations = {
    u'dns': ['do', 'mi', 'nus'],
    u'dūs': ['do', 'mi', 'nus'],
    u'dne': ['do', 'mi', 'ne'],
    u'alla': ['al', 'le', 'lu', 'ia'],
    u'xpc': ['xp', 'ic', 'tuc'],
    u'^': ['us'],
    u'ā': ['am'],
    u'ē': ['em'],
    u'ū': ['um'],
    u'ō': ['om']
}


class CharBox(object):
    __slots__ = ['char', 'ul', 'lr', 'ulx', 'lrx', 'uly', 'lry', 'width', 'height']

    def __init__(self, char, ul=None, lr=None):

        self.char = char
        if (ul is None) or (lr is None):
            self.ul = None
            self.lr = None
            return
        self.ul = tuple(ul)
        self.lr = tuple(lr)
        self.ulx = ul[0]
        self.lrx = lr[0]
        self.uly = ul[1]
        self.lry = lr[1]
        self.width = lr[0] - ul[0]
        self.height = lr[1] - ul[1]

    def __repr__(self):
        if self.ul and self.lr:
            return 'CharBox: \'{}\' at {}, {}'.format(self.char, self.ul, self.lr)
        else:
            return 'CharBox: \'{}\' empty'.format(self.char)


def clean_special_chars(inp):
    '''
    removes some special characters from OCR output. ideally these would be useful but not clear how
    best to integrate them into the alignment algorithm.
    '''
    inp = inp.replace('~', '')
    # inp = inp.replace('\xc4\x81', 'a')
    # inp = inp.replace('\xc4\x93', 'e')
    # # there is no i with bar above in unicode (???)
    # inp = inp.replace('\xc5\x8d', 'o')
    # inp = inp.replace('\xc5\xab', 'u')
    return inp


def recognize_text_strips(img, line_strips, ocr_model_name, verbose=False):
    '''
    takes in an image and a list of bounding boxes around text strips, extracts these strips, and
    performs OCR on the resulting set of strips. returns results character-by-character within CharBoxes.
    '''

    dir = os.path.dirname(__file__)
    ocr_model_path = os.path.join(dir, 'models/{}'.format(ocr_model_name))

    predictor = Predictor(checkpoint=ocr_model_path, processes=1)
    img_white_back = (1 - img).astype(float)

    # x, y, width, height
    strips = []
    for ls in line_strips:
        x, y, w, h = ls
        strip = img_white_back[y:y + h, x:x + w]
        strips.append(strip)

    results = []
    for r in predictor.predict_raw(strips, progress_bar=False):
        results.append(r)

    all_chars = []

    # iterate over results and make charbox objects out of every character
    for i, cs in enumerate(line_strips):

        strip_x_min, strip_y_min, strip_width, strip_height = cs
        res_line = [
            CharBox(
                clean_special_chars(x.chars[0].char),
                (x.global_start + strip_x_min, strip_y_min),
                (x.global_end + strip_x_min, strip_y_min + strip_height))
            for x in results[i].prediction.positions
            ]

        all_chars += res_line

    # remove all chars that are empty or otherwise invalid
    all_chars = list(filter(lambda x: x.char not in ['', '~'], all_chars))

    return all_chars


def handle_abbreviations(all_chars, max_iters=10e4):
    '''
    replace abbreviations found in the ocr with their expanded forms so they can be matched to the
    original text, when found (e.g. dns -> do mi nus)
    '''
    for abb in abbreviations.keys():
        iter = 0
        while True:
            ocr_str = ''.join(str(x.char) for x in all_chars)
            idx = ocr_str.find(abb)

            iter += 1
            if idx == -1 or iter > max_iters:
                # move on if this abbreviation no longer appears or if iterating too long
                break

            ins = []
            for i, segment in enumerate(abbreviations[abb]):
                split_box = all_chars[i + idx]
                ins += [CharBox(x, split_box.ul, split_box.lr) for x in segment]

            # insert new charboxes in the place of the charbox that should be abbreviated
            all_chars = all_chars[:idx] + ins + all_chars[idx + len(abb):]

    return all_chars


if __name__ == '__main__':

    import image_preprocessing as preproc
    from skimage import io

    fname = 'salzinnes_378'
    raw_image = io.imread('./png/{}_text.png'.format(fname))

    img_bin, img_eroded, angle = preproc.preprocess_images(raw_image)
    line_strips, lines_peak_locs, proj = preproc.identify_text_lines(img_eroded)

    ocr_model_name = 'salzinnes-gothic-2019'

    all_chars = recognize_text_strips(img_bin, line_strips, ocr_model_name, True)
    all_chars = handle_abbreviations(all_chars, max_iters=10e4)
