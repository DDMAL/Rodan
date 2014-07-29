import os
import re
import tempfile
import subprocess
import shutil
from django.core.files import File
from celery import task
from rodan.models.runjob import RunJob
from rodan.models.result import Result

valid_extensions = [".pdf", ".zip", ".jpg", ".jpeg", ".tif", ".tiff", ".JPG", ".JPEG", ".TIF", ".TIFF", ".PDF", '.png', '.PNG']
PATH_TO_KDU = "/usr/local/bin/kdu_compress"
PATH_TO_VIPS = "/usr/local/bin/vips"
JOB_NAME = "diva.conversion.to_jpeg2000"


@task(ignore_result=True, name=JOB_NAME)
def convert_to_diva(result_id, runjob_id, *args, **kwargs):
    runjob = RunJob.objects.get(pk=runjob_id)

    if result_id is None:
        page = runjob.page.compat_file_path
    else:
        result = Result.objects.get(result_id)
        page = result.result.path

    new_result = Result(run_job=runjob)
    new_result.save()

    result_save_path = new_result.result_path

    tdir = tempfile.mkdtemp()
    # some tiff files are corrupted, causing KDU to bail.
    # We'll take the safe route and convert all files, TIFF or not.
    name = os.path.basename(page)
    name, ext = os.path.splitext(name)

    tfile = os.path.join(tdir, "{0}.tiff".format(name))

    subprocess.call([PATH_TO_VIPS,
                    "im_copy",
                    page,
                    tfile])

    result_file = "{0}.jpx".format(name)
    output_file = os.path.join(tdir, result_file)

    subprocess.call([PATH_TO_KDU,
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

    f = open(output_file, 'rb')
    new_result.result.save(os.path.join(result_save_path, result_file), File(f))
    f.close()
    # debugging
    # shutil.move(tfile, result_save_path)
    shutil.rmtree(tdir)

    return str(new_result.uuid)
