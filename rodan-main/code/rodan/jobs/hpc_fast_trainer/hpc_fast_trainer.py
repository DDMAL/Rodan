from celery.utils.log import get_task_logger
from rodan.jobs.base import RodanTask
from rodan.models import Input
from django.conf import settings as rodan_settings
from uuid import uuid4
import base64
import json
import os
try:
    import pika
except ImportError:
    pass

class HPCFastTrainer(RodanTask):
    name = "Training model for Patchwise Analysis of Music Document - HPC"
    author = "Juliette Regimbal"
    description = "Performs the fast trainer job on Compute Canada Cedar"
    enabled = True
    category = "OMR - Layout analysis"
    interactive = False

    logger = get_task_logger(__name__)
    result_dict = None

    settings = {
        'title': 'Training parameters',
        'type': 'object',
        'job_queue': 'Python3',
        'properties': {
            'Maximum number of training epochs': {
                'type': 'integer',
                'minimum': 1,
                'default': 15
            },
            'Maximum number of samples per label': {
                'type': 'integer',
                'minimum': 100,
                'default': 10000
            },
            'Patch height': {
                'type': 'integer',
                'minimum': 64,
                'default': 256
            },
            'Patch width': {
                'type': 'integer',
                'minimum': 64,
                'default': 256
            },
            'Maximum time (D-HH:MM)': {
                'type': 'string',
                'default': '0-06:00'
            },
            'Maximum memory (MB)': {
                'type': 'integer',
                'minimum': 1024,
                'default': 257000
            },
            'CPUs': {
                'type': 'integer',
                'minimum': 1,
                'default': 6
            },
            'Slurm Notification Email': {
                'type': 'string',
                'default': ''
            }
        }
    }

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgb+png', 'image/rgb+jpg']},
        {'name': 'rgba PNG - Selected regions', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Background layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        # {'name': 'rgba PNG - Music symbol layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        # {'name': 'rgba PNG - Staff lines layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        # {'name': 'rgba PNG - Text', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 0', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 1', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
    )

    output_port_types = (
        {'name': 'Background Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        # {'name': 'Music Symbol Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        # {'name': 'Staff Lines Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        # {'name': 'Text Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 0', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 1', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
    )

    def _inputs(self, runjob, with_urls=True):
        """
        Return a dictionary of list of input file path and input resource type.
        If with_urls=True, it also includes the resource url and thumbnail urls.
        """
        def _extract_resource(resource, resource_type_mimetype=None):
            r = {'resource_path': str(resource.resource_file.path),  # convert 'unicode' object to 'str' object for consistency
                 'resource_type': str(resource_type_mimetype or resource.resource_type.mimetype)}
            if with_urls:
                r['resource_url'] = str(resource.resource_url)
                r['diva_object_data'] = str(resource.diva_json_url)
                r['diva_iip_server'] = getattr(rodan_settings, 'IIPSRV_URL')
                r['diva_image_dir'] = str(resource.diva_image_dir)
            return r

        input_objs = Input.objects.filter(run_job=runjob).select_related('resource', 'resource__resource_type', 'resource_list').prefetch_related('resource_list__resources')

        inputs = {}
        for input in input_objs:
            ipt_name = str(input.input_port_type_name)
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            if input.resource is not None:  # If resource
                inputs[ipt_name].append(_extract_resource(input.resource))
            elif input.resource_list is not None:  # If resource_list
                inputs[ipt_name].append(map(lambda x: _extract_resource(x, input.resource_list.resource_type.mimetype), input.resource_list.resources.all()))
            else:
                raise RuntimeError("Cannot find any resource or resource list on Input {0}".format(input.uuid))
        return inputs

    def run_my_task(self, inputs, settings, outputs):
        # Fail if arbitrary layers are not equal before training occurs.
        input_ports = len([x for x in inputs if x[:17] == 'rgba PNG - Layer '])
        output_ports = len([x for x in outputs if x[:5] == 'Model'])
        if input_ports != output_ports:
            raise Exception(
                'The number of input layers "rgba PNG - Layers" does not match the number of'
                ' output "Models"\n'
                'input_ports: %d output_ports: %d' % (input_ports, output_ports)
            )

        input = {}
        input['Image'] = inputs['Image'][0]['resource_url']
        input['Background'] = inputs['rgba PNG - Background layer'][0]['resource_url']
        input['Selected Regions'] = inputs['rgba PNG - Selected regions'][0]['resource_url']
        # input['Music Layer'] = inputs['rgba PNG - Music symbol layer'][0]['resource_url']
        # input['Staff Layer'] = inputs['rgba PNG - Staff lines layer'][0]['resource_url']
        # input['Text'] = inputs['rgba PNG - Text'][0]['resource_url']

        # Populate use-defined layers
        for i in range(input_ports):
            layer = 'rgba PNG - Layer %d' % i
            input[layer] = inputs[layer][0]['resource_url']

        # Optional ports
        # for k in inputs:
        #     if k == 'rgba PNG - Staff lines layer':
        #         input['Staff Layer'] = inputs['rgba PNG - Staff lines layer'][0]['resource_url']
        #     if k == 'rgba PNG - Text':
        #         input['Text'] = inputs['rgba PNG - Text'][0]['resource_url']

        message_dict = {
            'inputs': input,
            'settings': settings
        }
        message = json.dumps(message_dict)

        credentials = pika.PlainCredentials(os.environ['HPC_RABBITMQ_USER'], os.environ['HPC_RABBITMQ_PASSWORD'])
        parameters = pika.ConnectionParameters(os.environ['HPC_RABBITMQ_HOST'], 5672, '/', credentials)
        self.logger.info("Preparing to connect...")

        with pika.BlockingConnection(parameters) as conn:
            # Open Channel
            channel = conn.channel()
            channel.confirm_delivery()
            channel.queue_declare(queue='hpc-jobs')
            channel.queue_declare(queue='hpc-results')
            # Declare anonymous reply queue
            # result = channel.queue_declare(queue='', exclusive=True)
            # callback_queue = result.method.queue
            callback_queue = 'hpc-results'
            correlation_id = str(uuid4())
            # Send Message
            channel.basic_publish(
                exchange='',
                routing_key='hpc-jobs',
                properties=pika.BasicProperties(
                    reply_to=callback_queue,
                    correlation_id=correlation_id
                    ),
                body=message
            )
            self.logger.info("Message sent. Start waiting for reply")

            # define consumer callback
            def callback(channel, method_frame, header_frame, body):
                self.logger.info(method_frame.delivery_tag)
                self.logger.info(body)
                if method_frame and correlation_id == header_frame.correlation_id:
                    self.logger.info("Good!")
                    channel.basic_ack(method_frame.delivery_tag)
                    self.result_dict = json.loads(body.decode('utf-8'))
                    channel.basic_cancel(method_frame.consumer_tag)
                else:
                    self.logger.info("Cannot handle id {}".format(correlation_id))
                    channel.basic_nack(method_frame.delivery_tag)

            channel.basic_consume(callback_queue, callback)
            channel.start_consuming()

        self.logger.info(self.result_dict)
        if "error" in self.result_dict:
            self.my_error_information(
                None,
                (
                    "The request to Cedar failed with response: {0}\n"
                    "Try adding more memory and run the job again."
                ).format(self.result_dict["error"])
            )
            return False

        with open(outputs['Background Model'][0]['resource_path'], 'wb') as f:
            f.write(base64.decodebytes(self.result_dict['Background Model'].encode('utf-8')))
        # with open(outputs['Music Symbol Model'][0]['resource_path'], 'wb') as f:
        #     f.write(base64.decodebytes(self.result_dict['Music Symbol Model'].encode('utf-8')))
        # with open(outputs['Staff Lines Model'][0]['resource_path'], 'wb') as f:
        #     f.write(base64.decodebytes(self.result_dict['Staff Lines Model'].encode('utf-8')))
        # with open(outputs['Text Model'][0]['resource_path'], 'wb') as f:
        #     f.write(base64.decodebytes(self.result_dict['Text Model'].encode('utf-8')))
        for i in range(output_ports):
            layer = 'Model %d' % i
            with open(outputs[layer][0]['resource_path'], 'wb') as f:
                f.write(base64.decodebytes(self.result_dict[layer].encode('utf-8')))

        return True

    def my_error_information(self, exc, traceback):
        self.error_summary = 'HPC Fast Trainer - Something went very wrong'
        self.error_details = traceback