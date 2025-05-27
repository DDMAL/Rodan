from rodan.jobs.base import RodanTask


class HelloWorld(RodanTask):
    name = 'Hello World'
    author = 'Ryan Bannon'
    description = 'Output string "Hello World"'
    settings = {}
    enabled = True
    category = "Test"
    interactive = False

    input_port_types = (
        {'name': 'Text input', 'minimum': 0, 'maximum': 1, 'resource_types': ['text/plain']},
    )
    output_port_types = (
        {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
    )

    def run_my_task(self, inputs, settings, outputs):
        outfile_path = outputs['Text output'][0]['resource_path']
        outfile = open(outfile_path, "w")
        if 'Text input' in inputs:
            infile_path = inputs['Text input'][0]['resource_path']
            infile = open(infile_path, "r")
            outfile.write(("Hello World {0}").format(infile.read()))
            infile.close()
        else:
            outfile.write("Hello World")
        outfile.close()
        return True

    def test_my_task(self, testcase):
        inputs = {}
        outputs = {
            "Text output": [{"resource_types":"text/plain", "resource_path":testcase.new_available_path()}]
        }
        settings = {}

        self.run_my_task(inputs, settings, outputs)

        # The "Hello World" string should be written inside the output
        with open(outputs["Text output"][0]['resource_path'], "r") as fp:
            written_string = [l.strip() for l in fp.readlines()]

        # There's only one line
        testcase.assertEqual(len(written_string), 1)
        # and it should be "Hello World"
        testcase.assertEqual(written_string[0], "Hello World")


class HelloWorldMultiPort(RodanTask):
    name = 'Hello World Multiple Ports'
    author = 'Studio theYANG'
    description = 'Concatenate all input files and append "Hello World MultiPort"'
    settings = {}
    enabled = True
    category = "Test"
    interactive = False

    input_port_types = (
        {
            'name': 'Text input',
            'minimum': 0,
            'maximum': 10,
            'resource_types': ['text/plain']
        },
    )
    output_port_types = (
        {
            'name': 'Text output',
            'minimum': 1,
            'maximum': 10,
            'resource_types': ['text/plain']
        },
    )

    def run_my_task(self, inputs, settings, outputs):
        concatenated = ""
        for input_type in inputs:
            for input in inputs[input_type]:
                with open(input["resource_path"], "r") as infile:
                    concatenated += infile.read() + "\n"

        for output_type in outputs:
            for output in outputs[output_type]:
                with open(output["resource_path"], "w") as outfile:
                    outfile.write(concatenated)
                    outfile.write("Hello World MultiPort")

    def test_my_task(self, testcase):
        inputs = {}
        outputs = {
            "Text output": [
                {"resource_types":"text/plain", "resource_path":testcase.new_available_path()},
                {"resource_types":"text/plain", "resource_path":testcase.new_available_path()},
                {"resource_types":"text/plain", "resource_path":testcase.new_available_path()}
            ]
        }
        settings = {}
        self.run_my_task(inputs, settings, outputs)

        paths = [p["resource_path"] for p in outputs["Text output"]]
        for path in paths:
            # The "Hello World MultiPort" string should be written inside the output
            with open(path, "r") as fp:
                written_string = [l.strip() for l in fp.readlines()]

            # There's only one line
            testcase.assertEqual(len(written_string), 1)
            # and it should be "Hello World MultiPort"
            testcase.assertEqual(written_string[0], "Hello World MultiPort")

class HelloWorld3(RodanTask):
    name = 'Hello World - Python3'
    author = 'Alex Daigle'
    description = 'Output string "Hello World", using a different celery queue. '
    description += 'All you need is to specify the job_queue in the settings dictionary.'

    settings = {'job_queue': 'Python3'}
    enabled = True
    category = "Test"
    interactive = False

    input_port_types = (
        {'name': 'Text input', 'minimum': 0, 'maximum': 1, 'resource_types': ['text/plain']},
    )
    output_port_types = (
        {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
    )

    def run_my_task(self, inputs, settings, outputs):
        outfile_path = outputs['Text output'][0]['resource_path']
        outfile = open(outfile_path, "w")
        if 'Text input' in inputs:
            infile_path = inputs['Text input'][0]['resource_path']
            infile = open(infile_path, "r")
            outfile.write(("Hello World {0}").format(infile.read()))
            infile.close()
        else:
            outfile.write("Hello World")
        outfile.close()
        return True

    def test_my_task(self, testcase):
        inputs = {}
        outputs = {
            "Text output": [{"resource_types":"text/plain", "resource_path":testcase.new_available_path()}]
        }
        settings = {}

        self.run_my_task(inputs, settings, outputs)

        # The "Hello World" string should be written inside the output
        with open(outputs["Text output"][0]['resource_path'], "r") as fp:
            written_string = [l.strip() for l in fp.readlines()]

        # There's only one line
        testcase.assertEqual(len(written_string), 1)
        # and it should be "Hello World"
        testcase.assertEqual(written_string[0], "Hello World")

# class HelloWorldInteractive(RodanTask):
#     name = 'Hello World Interactive'
#     author = 'Ryan Bannon'
#     description = 'Interactive "Hello World"'
#     settings = {}
#     enabled = True
#     category = 'Test'
#     interactive = True
#     input_port_types = (
#         {'name': 'Text input', 'minimum': 0, 'maximum': 1, 'resource_types': ['text/plain']},
#     )
#     output_port_types = (
#         {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
#     )

#     def get_my_interface(self, inputs, settings):
# 	    # Get input.
#         input = 'there was no user input file'
#         if 'Text input' in inputs:
#             infile_path = inputs['Text input'][0]['resource_path']
#             with open(infile_path, "r") as infile:
#                 input = infile.read()

#         # Create data to pass.
#         data = {'input': input}
#         return ('interface.html', data)

#     def run_my_task(self, inputs, settings, outputs):
#         if '@done' not in settings:
#             return self.WAITING_FOR_INPUT()
#         outfile_path = outputs['Text output'][0]['resource_path']
#         with open(outfile_path, "w") as outfile:
#             outfile.write(("Hello World {0}").format(settings['@user_input']))
#         return True

#     def validate_my_user_input(self, inputs, settings, user_input):
#         return { '@done': True, '@user_input': user_input['user_input'] }

#     def my_error_information(self, exc, traceback):
#         pass
