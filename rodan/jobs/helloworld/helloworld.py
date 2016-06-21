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
    )
    output_port_types = (
        {'name': 'Text output', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
    )

    def run_my_task(self, inputs, settings, outputs):
        outfile = outputs['Text output'][0]['resource_path']
	text_file = open(outfile, "w")
	text_file.write("Hello World")
	text_file.close()
        return True
