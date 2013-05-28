import os
import uuid
import tempfile
import shutil
from django.core.files import File
from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from rodan.helpers.thumbnails import create_thumbnails
from gamera.core import init_gamera, load_image  # , save image?
import PIL, Image, ImageDraw
from gamera.plugins.pil_io import from_pil

JOB_NAME_AUTO = 'gamera.custom.border_removal.auto_border_removal'
JOB_NAME_CROP_BR = 'gamera.custom.border_removal.crop_border_removal'

def create_mask(org_img, ulx=0, uly=0, lrx=0, lry=0, imw=0):
    
    if 0==imw:
        scale_factor = 1
    else:
        scale_factor = float(org_img.ncols) / float(imw)

    print ulx, uly, lrx, lry, scale_factor

    arg_ulx = scale_factor * ulx
    arg_uly = scale_factor * uly
    arg_lrx = scale_factor * lrx - 1
    arg_lry = scale_factor * lry - 1

    if arg_ulx < 0:
        arg_ulx = 0
    if arg_ulx > org_img.ncols:
        arg_ulx = org_img.ncols

    if arg_lrx < 0:
        arg_lrx = 0
    if arg_lrx > (org_img.ncols - 1):
        arg_lrx = org_img.ncols - 1

    if arg_uly < 0:
        arg_uly = 0
    if arg_uly > org_img.nrows:
        arg_uly = org_img.nrows

    if arg_lry < 0:
        arg_lry = 0
    if arg_lry > (org_img.nrows - 1):
        arg_lry = org_img.nrows - 1
        
    im = Image.new('L', (org_img.ncols, org_img.nrows), color = 'white')
    draw = ImageDraw.Draw(im)
    draw.rectangle((arg_ulx, arg_uly, arg_lrx, arg_lry), fill='black')
    del draw

    im = from_pil(im)
    return im.to_onebit()

class AutoBorderRemovalTask(Task):
    max_retries = None
    name = JOB_NAME_AUTO

    def run(self, result_id, runjob_id, *args, **kwargs):
        #Guess what? I'm running.
        runjob = RunJob.objects.get(pk=runjob_id)
        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        #Get appropriate page
        if result_id is None:
            # this is the first job in a run
            page = runjob.page.compat_file_path
        else:
            # we take the page image we want to operate on from the previous result object
            result = Result.objects.get(pk=result_id)
            page = result.result.path

        #Initialize the result
        new_result = Result(run_job=runjob)
        new_result.save()

        result_save_path = new_result.result_path

        #Get the settings. Note that the runtime value is passed inside the 'default' field.
        settings = {}
        for s in runjob.job_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
            settings[setting_name] = setting_value

        #Gamera methods begins here
        init_gamera()

        task_image = load_image(page)
        grey_image = task_image.to_greyscale()
        tdir = tempfile.mkdtemp()

        crop_mask = grey_image.border_removal(**settings)
        result_image = task_image.mask(crop_mask)
        result_file = "{0}.png".format(str(uuid.uuid4()))
        result_image.save_image(os.path.join(tdir, result_file))

        #Copy over temp file to appropriate result path, and delete temps.
        f = open(os.path.join(tdir, result_file))
        new_result.result.save(os.path.join(result_save_path, result_file), File(f))
        f.close()
        shutil.rmtree(tdir)

        return str(new_result.uuid)

    def on_success(self, retval, task_id, args, kwargs):
        # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()


        res = create_thumbnails.s(result)
        res.apply_async()

    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()


class CropBorderRemovalTask(Task):
    max_retries = None
    name = JOB_NAME_CROP_BR

    def run(self, result_id, runjob_id, *args, **kwargs):
        #Guess what? I'm running.
        runjob = RunJob.objects.get(pk=runjob_id)
        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        # fall through to retrying if we're waiting for input
        if runjob.needs_input:
            runjob.status = RunJobStatus.WAITING_FOR_INPUT
            runjob.save()
            self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        if runjob.status == RunJobStatus.WAITING_FOR_INPUT:
            runjob.status = RunJobStatus.RUNNING
            runjob.save()

        #Get appropriate page
        if result_id is None:
            # this is the first job in a run
            page = runjob.page.compat_file_path
        else:
            # we take the page image we want to operate on from the previous result object
            result = Result.objects.get(pk=result_id)
            page = result.result.path

        #Initialize the result
        new_result = Result(run_job=runjob)
        new_result.save()

        result_save_path = new_result.result_path

        #Get the settings. Note that the runtime value is passed inside the 'default' field.
        settings = {}
        for s in runjob.job_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
            settings[setting_name] = setting_value

        init_gamera()
        task_image = load_image(page)

        tdir = tempfile.mkdtemp()
        crop_mask = create_mask(task_image, **settings)
        result_image = task_image.mask(crop_mask)
        result_file = "{0}.png".format(str(uuid.uuid4()))
        result_image.save_image(os.path.join(tdir, result_file))

        #Copy over temp file to appropriate result path, and delete temps.
        f = open(os.path.join(tdir, result_file))
        new_result.result.save(os.path.join(result_save_path, result_file), File(f))
        f.close()
        shutil.rmtree(tdir)

        return str(new_result.uuid)


    def on_success(self, retval, task_id, args, kwargs):
        # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()


        res = create_thumbnails.s(result)
        res.apply_async()

    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()
