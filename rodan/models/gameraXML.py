import os
import re
import png
import StringIO
import base64

from lxml import etree

# Note about class structure:  I'd like GameraXML to
# - inherit Model
# - define uuid and name
# because those are common to Classifier and PageGlyphs, but I get:
# TypeError: Error when calling the metaclass bases
# Cannot create a consistent method resolution


class GameraXML(object):

    class Meta:
        app_label = 'rodan'

    #(ABSTRACT)
    #@property
    #def directory_path(self):

    # GameraXML is expected to be subclassed and 'directory_path' is expected to be implemented
    # in the subclass.

    # I don't know the python-y way to communicate that.  Since python is keen on
    # gentlemanly agreements about scope, I'm going to let the above comment suffice.

    @property
    def file_path(self):
        return os.path.join(self.directory_path, "{0}.xml".format(str(self.uuid)))

    @property
    def glyphs(self):
        """ Makes a dictionary out of the gamera XML and returns it.
        See the footnote for the dictionary's structure.
        With one exception, all of the values of the dictionary are strings
        right from the XML.  The exception is the 'data' field which is
        converted from Gamera's runlength encoding to PNG."""

        parser = etree.XMLParser(resolve_entities=True)
        xml = etree.parse(open(self.file_path, 'r'), parser)
        glyphs = []

        for glyph in xml.xpath("//glyph"):
            # Keep values as strings, they'll just need to be
            # displayed anyway.

            # TODO: This only works if all of the fields are in the
            # XML.  Add support for missing fields
            #  (features or id element)
            # Perhaps there should be an argument in the API to generate features or not.
            ids = glyph.find('ids')
            id_element = ids.find('id')
            features = glyph.find('features')  # 'features' element
            #if (features):
            #    feature_list = features.getchildren()  # list of 'feature' elements
            #else:
            #    feature_list = []
            if features is not None:
                feature_list = features.getchildren()
            else:
                feature_list = []
            # or: features.xpath("feature")
            glyph_dict = {
                'ulx': float(glyph.get('ulx')),
                'uly': float(glyph.get('uly')),
                'nrows': float(glyph.get('nrows')),
                'ncols': float(glyph.get('ncols')),
                # Commented out code: Decided to go with a flatter structure than the XML
                # 'ids': {
                #     'state': ids.get('state'),
                #     'id': {
                #         'name': id_element.get('name'),
                #         'confidence': id_element.get('confidence')
                #     }
                # },
                'id_state': ids.get('state'),  # When state is UNCLASSIFIED, id_name and id_confidence don't exist in the xml
                                               # so use empty string and -1
                'id_name': id_element.get('name') if id_element is not None else "",
                'id_confidence': float(id_element.get('confidence')) if id_element is not None else -1,
                'data': self._base64_png_encode(glyph),
                'feature_scaling': float(features.get('scaling')) if id_element is not None else -1,
                'features': [{
                    'name': f.get('name'),
                    'values': [float(n) for n in f.text.split()]
                } for f in feature_list]
            }
            glyphs.append(glyph_dict)
        glyphs.sort(key=lambda glyph: glyph['id_name'])
            # Note: The client assumes that the glyphs are sorted.
            # It needs to do so to assign array controllers to each symbol.
        return glyphs

    def _create_new_xml(self):
        """ Called when a POST is received and a new object is created.
        """
        gamera_database = etree.XML(r'<gamera-database version="2.0" />')
        etree.SubElement(gamera_database, "glyphs")

        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

        f = open(self.file_path, 'w')
        f.write(etree.tostring(gamera_database, pretty_print=True, xml_declaration=True, encoding="utf-8"))
        return True

    def write_xml(self, glyphs):
        """ Intended to receive a PUT containing a Glyph in JSON.
        Writes XML.  Assume that I have a whole glyphs (array of
        glyph dictionaries) object as defined in the footnote. """

        gamera_database = etree.XML(r'<gamera-database version="2.0" />')
        glyphs_element = etree.SubElement(gamera_database, "glyphs")
        for json_glyph in glyphs:
            glyph_element = etree.SubElement(glyphs_element, "glyph",
                                             uly=str(json_glyph['uly']),
                                             ulx=str(json_glyph['ulx']),
                                             nrows=str(json_glyph['nrows']),
                                             ncols=str(json_glyph['ncols']))
            ids_element = etree.SubElement(glyph_element, "ids",
                                           state=json_glyph['id_state'])
            etree.SubElement(ids_element, "id",
                             name=json_glyph['id_name'],
                             confidence=str(json_glyph['id_confidence']))
            data_element = etree.SubElement(glyph_element, "data")
            data_element.text = self._runlength_encode(json_glyph['data'])
            features_element = etree.SubElement(glyph_element, "features",
                                                scaling=str(json_glyph['feature_scaling']))
            for feature in json_glyph['features']:
                f_element = etree.SubElement(features_element, "feature",
                                             name=feature['name'])
                                             #text=feature['values'])  # bad: need a string
                                             #text=''.join([val.append(' ') for val in feature['values']]) # Not understanding how awesome join is
                                             #text=' '.join(feature['values']) # bad: assigns an attribute called 'text'
                f_element.text = ' '.join([str(v) for v in feature['values']])
        f = open(self.file_path, 'w')
        f.write(etree.tostring(gamera_database, pretty_print=True, xml_declaration=True, encoding="utf-8"))
        return True

    def delete_xml(self):
        return os.remove(self.file_path)

    def _base64_png_encode(self, glyph):
        """ Takes an xpath glyph element and returns a png image of the
        glyph. """
        nrows = int(glyph.get('nrows'))
        ncols = int(glyph.get('ncols'))
        # Make an iterable that yields each row in boxed row flat pixel format:
        #   http://pypng.googlecode.com/svn/trunk/code/png.py
        # Method: Make a list of length nrows * ncols then after make sublists of
        # length ncols.
        pixels = []
        white_or_black = 255  # 255 is white
        for n in re.findall("\d+", glyph.find('data').text):
            pixels.extend([white_or_black] * int(n))
            white_or_black = white_or_black ^ 255  # Toggle between 0 and 255
        png_writer = png.Writer(width=ncols, height=nrows, greyscale=True)
        pixels_2D = []
        for i in xrange(nrows):
            pixels_2D.append(pixels[i*ncols: (i+1)*ncols])  # Index one row of pixels
        # StringIO.StringIO lets you write to strings as files: it gives you a file descriptor.
        # (pypng expects a file descriptor)
        buf = StringIO.StringIO()
        png_writer.write(buf, pixels_2D)
        return base64.b64encode(buf.getvalue())

    def _runlength_encode(self, base64_encoded_png):
        my_png = base64.b64decode(base64_encoded_png)
        buf = StringIO.StringIO(my_png)
        r = png.Reader(file=buf)  # Note: it gets confused if you don't name the argument
        r_out = r.read_flat()

        runlength_array = []
        previous_pixel = 255
        runlength = 0
        for pixel in r_out[2]:
            if (pixel == previous_pixel):
                runlength += 1
            else:
                runlength_array.append(runlength)
                runlength = 1
                previous_pixel = previous_pixel ^ 255  # Toggle between 0 and 255
        runlength_array.append(runlength)
        if (pixel == 255):
            runlength_array.append(0)
            # the last number must be the runlength of black pixels
            # so this case adds a zero if the bottom right pixel was white

        return ' '.join(map(str, runlength_array))
        # Returns a string containing each integer separated by spaces:
        # The 'map' call converts to an array of strings, then 'join' into one string



### GAMERA XML AS A DICTIONARY ###
# Glyph Object
#{
#    'ulx':
#    'uly':
#    'nrows':
#    'ncols':
#    'ids': {
#            'state':
#             'id': { 'name': 'confidence': }
#            }
#    'data': base64 encoded PNG
#    'feature_scaling':
#    'features': [
#                    {'name': name 'values': [split of text values]}
#                    ...
#                ]
#}

### IDS ###
# ids has a state and an id
# id has a name and a confidence
# I'm pretty sure you can only have one id in an ids thing.
# So why not change it to a single element?
# id: {'state': 'name': 'confidence'}
# Even better: Just fan it back into the glyph object

#{
#    'ulx':
#    'uly':
#    'nrows':
#    'ncols':
#    'id_state':
#    'id_name':
#    'id_confidence':
#    'data': base64 encoded PNG
#    'feature_scaling':
#    'features': [
#                    {'name': name 'values': [split of text values]}
#                    ...
#                ]
#}

# Do I need to write an XML schema and run it against a lot of gamera
# XML to ensure that it all follows my assumptions, especially
#  <ids> only has one <id> child
# I can't imagine a glyph having two states and names and
# confidences... so I don't need to.

# States can be
#  MANUAL AUTOMATIC HEURISTIC UNCLASSIFIED
# Example of unclassified:
#    <glyph uly="628" ulx="783" nrows="5" ncols="15">
#      <ids state="UNCLASSIFIED">
#      </ids>
#      <data>
#        1 13 1 45 1 13 1 0
#      </data>
#    </glyph>
# So, the schema might say
# - Required: ulx, uly, nrows, ncols, ids, data
# - ids is necessary but id is not if ids is UNCLASSIFIED
# - features are optional (along with feature_scaling)


# Glyph Object

### SYMBOLS ###
# There should also be a Symbol object
#<gamera-database version="2.0">
#  <symbols>
#    <symbol name="_group"/>
#    <symbol name="_group._part"/>
#    <symbol name="_group._part.clef.c"/>
#    <symbol name="_group._part.division.final"/>
# It's just a list of names.  Very simple.
# The symbols get saved when you save page glyphs.
# It can honesly just be a 1d array of strings.
