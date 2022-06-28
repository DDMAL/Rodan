import os
import sys

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

import json
import unittest
import xml.etree.ElementTree as ET
import build_mei_file as bmf
from pymei import MeiElement
from copy import copy


class TestMEIGlyphCreation(unittest.TestCase):

    punctum_xml = '<neume>  <nc/>  </neume>'
    podastus3_xml = '<neume>  <nc/>  <nc intm="2S"/> </neume>'
    clefc_xml = '<clef line="4" oct="None" pname="None" shape="C" />'
    oblique3_xml = '<neume> <nc ligated="true"/>  <nc intm="-3S" ligated="true"/> </neume>'

    punctum_glyph = {'bounding_box': {'lrx': 1010, 'lry': 1010, 'ulx': 1000, 'uly': 1000},
     'name': 'neume.punctum',
     'note': 'g',
     'octave': '2',
     'staff': '3',
     'strt_pos': '10',
     'system_begin': False}

    clefc_glyph = {'bounding_box': {'lrx': 1010, 'lry': 1010, 'ulx': 1000, 'uly': 1000},
     'name': 'clef.c',
     'note': 'None',
     'octave': 'None',
     'staff': '9',
     'strt_pos': '4',
     'system_begin': False}

    oblique3_glyph = {'bounding_box': {'lrx': 2648, 'lry': 5164, 'ulx': 2503, 'uly': 5040},
      'name': 'neume.oblique3',
      'note': 'b',
      'octave': '2',
      'staff': '14',
      'strt_pos': '8',
      'system_begin': False}

    def setUp(self):
        self.dummy_surface = MeiElement('surface')

    def test_punctum_primitive(self):
        xml = ET.fromstring(self.punctum_xml)[0]
        el = bmf.create_primitive_element(xml, self.punctum_glyph, 0, self.dummy_surface)

        # should return a simple MeiElement with a note, an octave, and a facsimile
        self.assertEqual(type(el), MeiElement)
        self.assertEqual(el.getAttribute('pname').value, self.punctum_glyph['note'])
        self.assertEqual(el.getAttribute('oct').value, self.punctum_glyph['octave'])

        # make sure there are no extraneous elements
        exp_atts = set(['pname', 'oct', 'facs'])
        res_atts = set([x.name for x in el.attributes])
        self.assertEqual(exp_atts, res_atts)

    def test_clefc_primitive(self):
        xml = ET.fromstring(self.clefc_xml)
        el = bmf.create_primitive_element(xml, self.clefc_glyph, 0, self.dummy_surface)

        # should return a simple MeiElement with a shape, an line, and a facsimile
        self.assertEqual(type(el), MeiElement)
        self.assertEqual(el.getAttribute('line').value, self.clefc_glyph['strt_pos'])

        # make sure there are no extraneous elements
        exp_atts = set(['line', 'shape', 'facs'])
        res_atts = set([x.name for x in el.attributes])
        self.assertEqual(exp_atts, res_atts)

    def test_oblique3_neume(self):
        dummy_classifier = {'neume.oblique3': ET.fromstring(self.oblique3_xml)}
        width_container = {'neume.oblique3': [1, 1]}
        el = bmf.glyph_to_element(dummy_classifier, width_container, self.oblique3_glyph, self.dummy_surface)

        # should return a single MeiElement with no attributes...
        self.assertEqual(type(el), MeiElement)
        self.assertEqual(el.getAttributes(), [])

        # ...and two children
        clds = el.getChildren()
        self.assertEqual(len(clds), 2)

    def test_resolve_interval(self):
        '''
        Test resolving an interval between two neume components and getting a pname/octave for each
        '''
        nc1 = MeiElement('nc')
        nc1.addAttribute('pname', 'c')
        nc1.addAttribute('oct', '2')

        # normal case
        nc2 = MeiElement('nc')
        nc2.addAttribute('intm', '2s')
        res = bmf.resolve_interval(nc1, nc2)
        self.assertEqual(res, ('e', '2'))

        # octave up
        nc2 = MeiElement('nc')
        nc2.addAttribute('intm', '7S')
        res = bmf.resolve_interval(nc1, nc2)
        self.assertEqual(res, ('c', '3'))

        # octave down
        nc2 = MeiElement('nc')
        nc2.addAttribute('intm', '-1s')
        res = bmf.resolve_interval(nc1, nc2)
        self.assertEqual(res, ('b', '1'))

        # invalid pitch
        nc3 = MeiElement('nc')
        nc3.addAttribute('pname', 'z')
        nc3.addAttribute('oct', '2')
        with self.assertRaises(ValueError) as context:
            res = bmf.resolve_interval(nc3, nc2)


if __name__ == '__main__':
    unittest.main()
