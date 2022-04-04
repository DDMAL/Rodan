import os

import shutil

import jsymbolic_utilities

from rodan.jobs.base import RodanTask
from django.conf import settings
from tempfile import mkdtemp
from music21 import *


class extract_features(RodanTask):
    name = 'jSymbolic Feature Extractor'
    author = 'Cory McKay and Tristano Tenaglia'
    description = 'Extract features from a music file using the jSymbolic feature extractor'
    settings = {}
    enabled = True
    category = "jSymbolic - Feature Extraction"
    interactive = False

    input_port_types = (
        {
            'name': 'jSymbolic Music File Input',
            'minimum': 1,
            'maximum': 1,
            # Note that musicXML resource is from the Rodan musicXML format and not specified in resource_types.yaml
            'resource_types': ['application/mei+xml', 'application/midi', 'application/x-musicxml+xml']
        },

        {
            'name': 'jSymbolic Configuration File Input',
            'minimum': 0,
            'maximum': 1,
            'resource_types': ['application/jsc+txt']
        },
    )
    output_port_types = (
        {
            'name': 'jSymbolic ACE XML Value Output',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/ace+xml']
        },

        {
            'name': 'jSymbolic ACE XML Definition Output',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/ace+xml']
        },

        {
            'name': 'jSymbolic Configuration File Output',
            'minimum': 0,
            'maximum': 1,
            'resource_types': ['application/jsc+txt']

        },

        {
            'name': 'jSymbolic ARFF Output',
            'minimum': 0,
            'maximum': 1,
            'resource_types': ['application/arff']
        },

        {
            'name': 'jSymbolic ARFF CSV Output',
            'minimum': 0,
            'maximum': 1,
            'resource_types': ['application/arff+csv']
        },
    )

    def run_my_task(self, inputs, job_settings, outputs):
        # Get the path of the jsymbolic jar on the system
        java_directory = settings.JSYMBOLIC_JAR
        jar_name = 'jSymbolic2.jar'

        music_file_type = inputs['jSymbolic Music File Input'][0]['resource_type']
        music_file = inputs['jSymbolic Music File Input'][0]['resource_path']
        abs_path = None
        if music_file_type == 'application/x-musicxml+xml':
            # If we have a musicXML file type, then convert to temp MIDI file for jSymbolic use
            abs_path = mkdtemp()
            music_file = os.path.join(abs_path, 'temp.midi')
            sc = converter.parse(inputs['jSymbolic Music File Input'][0]['resource_path'])
            sc.write('midi', music_file)

        config_file_path = None
        stderr_valid = None
        if 'jSymbolic Configuration File Input' in inputs:
            # Validate the configuration file
            config_file_path = inputs['jSymbolic Configuration File Input'][0]['resource_path']
            config_validate_input = ['java', '-jar', jar_name, '-validateconfigfeatureoption', config_file_path]
            return_valid, stdout_valid, stderr_valid = jsymbolic_utilities.execute(config_validate_input,
                                                                                   java_directory)

        # If configuration file is not valid then output the standard error to the user
        if stderr_valid:
            raise Exception(stderr_valid)

        if config_file_path:
            # If everything is valid in configuration file, then make sure CSV and ARFF are true
            # if they are not, then force to be true to accommodate Rodan output ports
            if 'jSymbolic ARFF Output' in outputs:
                arff_false = 'convert_to_arff=false'
                arff_true = 'convert_to_arff=true'
                jsymbolic_utilities.replace(config_file_path, arff_false, arff_true)

            if 'jSymbolic ARFF CSV Output' in outputs:
                csv_false = 'convert_to_csv=false'
                csv_true = 'convert_to_csv=true'
                jsymbolic_utilities.replace(config_file_path, csv_false, csv_true)

            # Run jsymbolic using the specified configuration file
            config_input = ['java', '-jar', jar_name, '-configrun', config_file_path, music_file,
                            outputs['jSymbolic ACE XML Value Output'][0]['resource_path'],
                            outputs['jSymbolic ACE XML Definition Output'][0]['resource_path']]
            return_value, stdout, stderr = jsymbolic_utilities.execute(config_input, java_directory)
        else:
            # Run jsymbolic default
            default_input = ['java', '-jar', jar_name, '-csv', '-arff', music_file,
                             outputs['jSymbolic ACE XML Value Output'][0]['resource_path'],
                             outputs['jSymbolic ACE XML Definition Output'][0]['resource_path']]
            return_value, stdout, stderr = jsymbolic_utilities.execute(default_input, java_directory)

        # Return if jsymbolic experienced an error so no further file processing is done
        if stderr:
            raise Exception(stderr)

        # Split up filename and extension for arff and csv files
        pre, ext = os.path.splitext(outputs['jSymbolic ACE XML Value Output'][0]['resource_path'])

        # Try to get arff file if it exists, otherwise continue
        if 'jSymbolic ARFF Output' in outputs:
            src_arff_file_path = "{0}.arff".format(pre)
            jsymbolic_utilities.copy_when_exists(src_arff_file_path,
                                                outputs['jSymbolic ARFF Output'][0]['resource_path'])

        # Try to get csv file if it exists, otherwise continue
        if 'jSymbolic ARFF CSV Output' in outputs:
            src_csv_file_path = "{0}.csv".format(pre)
            jsymbolic_utilities.copy_when_exists(src_csv_file_path,
                                                outputs['jSymbolic ARFF CSV Output'][0]['resource_path'])

        # Try to copy configuration file to output if one was specified
        if 'jSymbolic Configuration File Output' in outputs:
            jsymbolic_utilities.copy_when_exists(config_file_path,
                                                outputs['jSymbolic Configuration File Output'][0]['resource_path'])

        # Remove the temp directory for musicXML conversion
        if abs_path:
            shutil.rmtree(abs_path)

        return return_value

    def test_my_task(self, testcase):
        # No tests for now
        pass

    def my_error_information(self, exc, traceback):
        return {'error_summary': 'jSymbolic Standard Error', 'error_details': traceback}
