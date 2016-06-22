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
        if inputs is not None:
            infile_path = inputs['Text input'][0]['resource_path']
            infile = open(infile_path, "r")
            outfile.write(("Hello World {0}").format(infile.read()))
            infile.close()
        else:
            outfile.write("Hello World")
        outfile.close()
        return True
