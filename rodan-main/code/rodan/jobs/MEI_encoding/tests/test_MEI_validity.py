import os
import sys

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from lxml import etree
import unittest
import build_mei_file as bmf
import json
import parse_classifier_table as pct
from StringIO import StringIO

class TestMEIValidity(unittest.TestCase):

    # to be replaced with the neume schema when the clef/custos issue is resolved (hopefully)
    rng_path = './tests/resources/mei-all.rng'
    classifier_path = './tests/resources/square_notation_basic_classifier.csv'

    # i can't figure out how to elegantly parametrize this in python 2.7 without adding
    # dependencies that don't support python 2.7. hopefully i will move this code to python 3
    # and everything will be moot
    syls_path = './tests/resources/syls_salzinnes_304.json'
    pitches_path = './tests/resources/pitches_salzinnes_304.json'

    with open(rng_path) as file:
        relaxng_doc = etree.parse(file)
    rng = etree.RelaxNG(relaxng_doc)
    classifier = pct.fetch_table_from_csv(classifier_path)

    def setUp(self):
        with open(self.pitches_path) as file:
            self.jsomr = json.loads(file.read())
        with open(self.syls_path) as file:
            self.syls = json.loads(file.read())

    def test_build_mei(self):
        '''
        Ensures that the MEI file generated validates against the MEI RNG schema.
        '''
        mei_text = bmf.process(self.jsomr, self.syls, self.classifier, width_mult=1, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))
        self.assertTrue(self.rng.validate(mei_xml))

    def test_build_mei_no_merging(self):
        '''
        Ensures that the MEI file generated validates against the MEI RNG schema without merging
        neume components as a final step.
        '''
        mei_text = bmf.process(self.jsomr, self.syls, self.classifier, width_mult=0, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))
        self.assertTrue(self.rng.validate(mei_xml))

    def test_build_mei_no_syls(self):
        '''
        Ensures that the MEI file generated validates against the MEI RNG schema if syllables
        are not supplied.
        '''
        mei_text = bmf.process(self.jsomr, None, self.classifier, width_mult=1, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))
        self.assertTrue(self.rng.validate(mei_xml))

    def test_mei_remove_glyphs(self):
        '''
        Ensures that removing most of the glyphs from the pitch-finding output (all punctums)
        still results in a valid MEI file.
        '''
        new_g = [x for x in self.jsomr['glyphs'] if not ('punctum' in x['glyph']['name'])]
        self.jsomr['glyphs'] = new_g

        mei_text = bmf.process(self.jsomr, self.syls, self.classifier, width_mult=1, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))

        self.assertTrue(self.rng.validate(mei_xml))

    def test_mei_remove_syls(self):
        '''
        Ensures that removing most of the syllables (every other one) from the text-alignment output
        still results in a valid MEI file.
        '''
        new_s = [x for i, x in enumerate(self.syls['syl_boxes']) if not i % 2]
        self.syls['syl_boxes'] = new_s

        mei_text = bmf.process(self.jsomr, self.syls, self.classifier, width_mult=1, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))

        self.assertTrue(self.rng.validate(mei_xml))

    def test_mei_move_syl_boxes(self):
        '''
        Ensures that shifting each of the syl_boxes into an awkward position before neume-to-text
        alignment still results in a valid MEI file.
        '''
        sh_amt = int(self.syls['median_line_spacing'])

        # shift diagonally upwards and to the right
        for sb in self.syls['syl_boxes']:
            sb['lr'][0] -= sh_amt
            sb['lr'][1] += sh_amt
            sb['ul'][0] -= sh_amt
            sb['ul'][1] += sh_amt

        mei_text = bmf.process(self.jsomr, self.syls, self.classifier, width_mult=1, verbose=False)
        mei_xml = etree.parse(StringIO(mei_text))
        self.assertTrue(self.rng.validate(mei_xml))


if __name__ == '__main__':
    unittest.main()
