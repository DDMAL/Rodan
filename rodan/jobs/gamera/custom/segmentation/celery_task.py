import os
import uuid
import tempfile
import shutil
import json
from django.core.files import File
from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from rodan.helpers.thumbnails import create_thumbnails
from gamera.core import init_gamera, load_image
import Image, ImageDraw, ImageMath
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict

JOB_NAME = 'gamera.custom.segmentation.segmentation'


class SegmentationTask(Task):
    max_retries = None
    name = JOB_NAME

    def run(self, result_id, runjob_id, *args, **kwargs):
        # Set status to running
        runjob = RunJob.objects.get(pk=runjob_id)

        # The job has already run once. No need to generate polygons again.
        if runjob.status == RunJobStatus.RUN_ONCE_WAITING:
            if runjob.needs_input:
                self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        # This is the first time the job is running. Generate the polygons and save.
        elif runjob.needs_input:
            runjob.status = RunJobStatus.RUNNING
            runjob.save()

            # Get appropriate page
            if result_id is None:
                # this is the first job in a run
                page = runjob.page.compat_file_path
            else:
                # we take the page image we want to operate on from the previous result object
                result = Result.objects.get(pk=result_id)
                page = result.result.path

            init_gamera()

            task_image = load_image(page)

            ranked_page = task_image.rank(9, 9, 0)
            
            settings = {}
            for s in runjob.job_settings:
                setting_name = "_".join(s['name'].split(" "))
                setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
                settings[setting_name] = setting_value

            # delete these two extra settings since miyao staff-finder does not accept it.
            del settings['polygon_outer_points'], settings['image_width']

            staff_finder = StaffFinder_miyao(ranked_page, 0, 0)
            staff_finder.find_staves(**settings)

            poly_list = staff_finder.get_polygon()
            poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
            poly_json_list = create_polygon_outer_points_json_dict(poly_list)

            for setting in runjob.job_settings:
                if setting['name'] == 'polygon_outer_points':
                    setting['default'] = poly_json_list
                if setting['name'] == 'image_width':
                    setting['default'] = task_image.ncols

            runjob.status = RunJobStatus.RUN_ONCE_WAITING
            runjob.save()

            self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)


        # Now the job has all the required inputs and will do the masking.
        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        # Get appropriate page
        if result_id is None:
            # this is the first job in a run
            page = runjob.page.compat_file_path
        else:
            # we take the page image we want to operate on from the previous result object
            result = Result.objects.get(pk=result_id)
            page = result.result.path

        # Initialize the result
        new_result = Result(run_job=runjob)
        new_result.save()

        result_save_path = new_result.result_path

        # Get the settings. Note that the runtime value is passed inside the 'default' field.
        settings = {}
        for s in runjob.job_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
            settings[setting_name] = setting_value

        # init_gamera()
        task_image = Image.open(page)
        mask_img = Image.new('1', task_image.size, color=1)
        mask_drawer = ImageDraw.Draw(mask_img)

        try:
            polygon_data = json.loads(settings['polygon_outer_points'])
        except ValueError:
            # There's a problem in the JSON - it may be malformed, or empty
            polygon_data = []

        for polygon in polygon_data:
            flattened_poly = [j for i in polygon for j in i]
            mask_drawer.polygon(flattened_poly, outline=0, fill=0)

        del mask_drawer

        # The ImageMath expression is unfortunately a bit complicated, but it works, and works fast.
        result_image = ImageMath.eval('~(~a & ~b)', a=task_image, b=mask_img)

        tdir = tempfile.mkdtemp()
        result_file = "{0}.png".format(str(uuid.uuid4()))
        result_image.save(os.path.join(tdir, result_file))

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
