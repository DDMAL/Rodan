import os
import unittest

from rodan.jobs.resource_identification import fileparse


class MimeTypeTestCase(unittest.TestCase):
    #def test_all(self):
    #    base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"

    def test_ace(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "LLIA"), "application/ace+xml")

    def test_arff(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "AWKQ"), "application/arff")

    def test_arff_csv(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "XSNA"), "application/arff+csv")

    def test_gamera_polygons(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "ZHAH"), "application/gamera-polygons+txt")

    def test_gamera(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "DXUA"), "application/gamera+xml")

    def test_jsc(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "PKAF"), "application/jsc+txt")

    def test_mei(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "AHSK"), "application/mei+xml")

    def test_midi(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "PAOS"), "application/midi")

    def test_image_grey16(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "TQOA"), "image/grey16+png")

    def test_image_jp2(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "WYAG"), "image/jp2")

    def test_image_onebit(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "EQRQ"), "image/onebit+png")

    def test_image_rgb_0(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "YASH"), "image/rgb+jpg")

    def test_x_muscxml(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "GWJA"), "application/x-muscxml+xml")

    def test_zip(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "KASD"), "application/zip")

    def test_json_0(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "UZFA"), "application/json")

    def test_ocrupus(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "ZTAS"), "application/ocropus+pyrnn")

    def test_json_1(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "GAZG"), "application/json")

    def test_json_2(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "QIWR"), "application/json")

    def test_image_rgba(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "PXCV"), "image/rgba+png")

    def test_image_rgb_1(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "OASD"), "image/rgb+png")

    def test_keras_model(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "APFX"), "keras/model+hdf5")

    def test_text_csv(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(fileparse(base_directory + "2FKA"), "text/csv")

    def test_x_vix_figuredbass_pandas_series(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"

        self.assertEqual(
            fileparse(base_directory + "AOGO"), "application/x-vis_figuredbass_pandas_series+csv")

    def test_x_vis_horizontal_pandas_series(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(
            fileparse(base_directory + "DUKU"), "application/x-vis_horizontal_pandas_series+csv")

    def test_x_vis_vertical_pandas_series(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(
            fileparse(base_directory + "BYKA"), "application/x-vis_vertical_pandas_series+csv")

    def test_x_vis_ngram_pandas_dataframe(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(
            fileparse(base_directory + "7W4A"), "application/x-vis_ngram_pandas_dataframe+csv")

    def test_x_vis_noterest_pandas_series(self):
        base_directory = os.path.abspath(os.getcwd()) + "/rodan/test/files/"
        self.assertEqual(
            fileparse(base_directory + "KGRA"), "application/x-vis_noterest_pandas_series+csv")

