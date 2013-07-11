import os

from django.db import models
from lxml import etree
from uuidfield import UUIDField

from rodan.models.glyph import Glyph


class GameraXML(models.Model):

    class Meta:
        app_label = 'rodan'
        abstract = True

    def upload_path(self, filename):
        return self.file_path

    uuid = UUIDField(primary_key=True, auto=True)
    xml_file = models.FileField(upload_to=upload_path, null=True, max_length=255)

    #(ABSTRACT)
    #@property
    #def directory_path(self):

    # 'directory_path' is expected to be implemented in the subclass.

    @property
    def file_path(self):
        return os.path.join(self.directory_path, "{0}.xml".format(str(self.uuid)))

    @property
    def glyphs(self):
        xml = Glyph.xml_from_file(self.file_path)
        return [Glyph(g).__dict__ for g in xml.xpath("//glyph")]

    def _create_new_xml(self):
        """ Called when a POST is received.  A new object is created."""
        gamera_database = etree.XML(r'<gamera-database version="2.0" />')
        etree.SubElement(gamera_database, "glyphs")

        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

        self.write_xml_to_file(gamera_database)

    def write_json_glyphs_to_xml(self, json_glyphs):
        """ Called when a PATCH is received.  Rewrite xml with new glyphs."""

        gamera_database = etree.XML(r'<gamera-database version="2.0" />')
        glyphs_element = etree.SubElement(gamera_database, "glyphs")

        for json_glyph in json_glyphs:
            glyph_element = Glyph.xml_from_json(json_glyph)
            glyphs_element.append(glyph_element)

        self.write_xml_to_file(gamera_database)

    def delete_xml(self):
        return os.remove(self.file_path)

    def add_uuids_and_sort_glyphs(self):
        """Gives ids to all of the glyphs in the XML file."""
        xml = Glyph.xml_from_file(self.file_path)

        glyphs = xml.xpath("//glyphs")[0]
        glyphs[:] = sorted(glyphs, key=lambda glyph: Glyph.name_from_xml(glyph))

        for glyph in glyphs:
            if 'uuid' not in glyph.keys():
                glyph.set('uuid', Glyph.make_uuid())

        self.write_xml_to_file(xml)

    def write_xml_to_file(self, xml):
        with open(self.file_path, 'wb') as f:
            f.write(etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="utf-8"))
