import PIL.Image
import subprocess
import tempfile
import shutil
import os
from rodan.jobs.base import RodanTask
from django.conf import settings
from distutils.spawn import find_executable

# Find kdu_compress and graphicsmagick upon loading
BIN_KDU_COMPRESS = getattr(settings, 'BIN_KDU_COMPRESS', None) or find_executable('kdu_compress')
if not BIN_KDU_COMPRESS:
    raise ImportError("cannot find kdu_compress")

BIN_GM = getattr(settings, 'BIN_GM', None) or find_executable('gm')
if not BIN_GM:
    raise ImportError("cannot find gm")

class to_jpeg2000(RodanTask):
    name = 'rodan.jobs.conversion.to_jpeg2000'
    author = 'Andrew Hankinson'
    description = "Converts an image to a JPEG2000 image suitable for display in Diva"
    settings = {}
    enabled = True
    category = "Conversion"
    interactive = False

    input_port_types = ({'name': 'in',
                         'minimum': 1,
                         'maximum': 1,
                         'resource_types': lambda mime: mime.startswith('image/')}, )
    output_port_types = ({'name': 'out',
                          'minimum': 1,
                          'maximum': 1,
                          'resource_types': ['image/jp2']}, )

    def run_my_task(self, inputs, settings, outputs):
        task_image = inputs['in'][0]['resource_path']

        with self.tempdir() as tdir:
            name = os.path.basename(task_image)
            name, ext = os.path.splitext(name)
            tfile = os.path.join(tdir, "{0}.tiff".format(name))

            subprocess.check_call([BIN_GM,
                                   'convert',
                                   "-depth", "8",         # output RGB
                                   "-compress", "None",
                                   task_image,
                                   tfile])
            result_file = "{0}.jp2".format(name)
            output_file = os.path.join(tdir, result_file)


            subprocess.check_call([BIN_KDU_COMPRESS,
                                   "-i", tfile,
                                   "-o", output_file,
                                   "-quiet",
                                   "Clevels=5",
                                   "Cblk={64,64}",
                                   "Cprecincts={256,256},{256,256},{128,128}",
                                   "Creversible=yes",
                                   "Cuse_sop=yes",
                                   "Corder=LRCP",
                                   "ORGgen_plt=yes",
                                   "ORGtparts=R",
                                   "-rate", "-,1,0.5,0.25"])

            shutil.copyfile(output_file, outputs['out'][0]['resource_path'])

    def test_my_task(self, testcase):
        inputs = {
            'in': [
                {'resource_type': 'image/jpeg',
                 'resource_path': testcase.new_available_path()
                 }
            ]
        }
        PIL.Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['in'][0]['resource_path'], 'JPEG')
        outputs = {
            'out': [
                {'resource_type': 'image/jp2',
                 'resource_path': testcase.new_available_path()
                 }
            ]
        }

        self.run_my_task(inputs, {}, outputs)
        result = PIL.Image.open(outputs['out'][0]['resource_path'])
        testcase.assertEqual(result.format, 'JPEG2000')
