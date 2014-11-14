from gamera.core import init_gamera, load_image
from rodan.jobs.gamera import argconvert
from rodan.jobs.base import RodanTask


class GameraTask(RodanTask):
    abstract = True

    def process_image(self, task_image, settings):
        raise NotImplementedError()

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        settings = {}
        for s in rodan_job_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
            settings[setting_name] = setting_value

        init_gamera()

        task_image = load_image(inputs[inputs.keys()[0]][0]['resource_path'])
        result_image = self.process_image(task_image, settings)
        result_image.save_image(outputs[outputs.keys()[0]][0]['resource_path'])
