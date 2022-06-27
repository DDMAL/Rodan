from rodan.jobs.base import RodanTask


class test_rodan_task(RodanTask):
    name = "TestRodan"
    author = 'Kemal Kongar'
    description = 'Pass"'
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
        pass
