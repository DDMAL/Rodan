import os
import unittest

from rodan.jobs.resource_identification import fileparse


class MimeTypeTestCase(unittest.TestCase):
    def test_all(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"

        self.assertEqual(fileparse(base_directory + "LLIA"), "application/ace+xml")
        self.assertEqual(fileparse(base_directory + "AWKQ"), "application/arff")
        self.assertEqual(fileparse(base_directory + "XSNA"), "application/arff+csv")
        self.assertEqual(fileparse(base_directory + "ZHAH"), "application/gamera-polygons+txt")
        self.assertEqual(fileparse(base_directory + "DXUA"), "application/gamera+xml")
        self.assertEqual(fileparse(base_directory + "PKAF"), "application/jsc+txt")
        self.assertEqual(fileparse(base_directory + "AHSK"), "application/mei+xml")
        self.assertEqual(fileparse(base_directory + "PAOS"), "application/midi")
        self.assertEqual(fileparse(base_directory + "TQOA"), "image/grey16+png")
        self.assertEqual(fileparse(base_directory + "WYAG"), "image/jp2")
        self.assertEqual(fileparse(base_directory + "EQRQ"), "image/onebit+png")
        self.assertEqual(fileparse(base_directory + "YASH"), "image/rgb+jpg")
        self.assertEqual(fileparse(base_directory + "GWJA"), "application/x-muscxml+xml")
        self.assertEqual(
            fileparse(base_directory + "AOGO"), "application/x-vis_figuredbass_pandas_series+csv")
        self.assertEqual(
            fileparse(base_directory + "DUKU"), "application/x-vis_horizontal_pandas_series+csv")
        self.assertEqual(
            fileparse(base_directory + "BYKA"), "application/x-vis_vertical_pandas_series+csv")
        self.assertEqual(
            fileparse(base_directory + "7W4A"), "application/x-vis_ngram_pandas_dataframe+csv")
        self.assertEqual(
            fileparse(base_directory + "KGRA"), "application/x-vis_noterest_pandas_series+csv")
        self.assertEqual(fileparse(base_directory + "KASD"), "application/zip")
        self.assertEqual(fileparse(base_directory + "UZFA"), "application/json")
        self.assertEqual(fileparse(base_directory + "ZTAS"), "application/ocropus+pyrnn")
        self.assertEqual(fileparse(base_directory + "GAZG"), "application/json")
        self.assertEqual(fileparse(base_directory + "QIWR"), "application/json")
