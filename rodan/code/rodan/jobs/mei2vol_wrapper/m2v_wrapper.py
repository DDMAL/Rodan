from rodan.jobs.base import RodanTask

# avoid python 2/3 conflict in Rodan
try:
    from . import mei2volpiano
except (SystemError, ImportError, SyntaxError):
    pass

# Rodan job
class MEI2Vol(RodanTask):
    name = "MEI2Volpiano"
    author = "Ravi Raina, Kemal Kongar, & Gabrielle Halpin"
    description = "Converts MEI or XML files into volpiano strings."
    settings = {
        "title": "Parameters",
        "type": "object",
        "job_queue": "Python3",
        "properties": {"Output": {"type": "string", "default": ""}},
    }
    enabled = True
    category = "Type conversion"
    interactive = False

    input_port_types = [
        {
            "name": "MEI",
            "minimum": 1,
            "maximum": 1, 
            "resource_types": ["application/mei+xml"],
        }
    ]

    output_port_types = [
        {
            "name": "Volpiano",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["text/plain"],
        }
    ]

    # Runs the MEI2Volpiano conversion and returns a txt file output
    def run_my_task(self, inputs, settings, outputs):
        lib = mei2volpiano.MEItoVolpiano()
        outfile_path = outputs['Volpiano'][0]['resource_path']
        outfile = open(outfile_path, "w")
        if 'MEI' in inputs:
            infile_path = inputs['MEI'][0]['resource_path']
            infile = open(infile_path, "r")
            volpiano = lib.convert_mei_volpiano(infile)
            outfile.write(volpiano)
            infile.close()
        else:
            outfile.write("Could not write properly.")
        outfile.close()
        
        return True