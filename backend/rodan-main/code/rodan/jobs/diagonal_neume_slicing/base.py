from ast import Import
from rodan.jobs.base import RodanTask
try:
    from gamera.core import init_gamera, Image, load_image
    from gamera import gamera_xml

    from .ProjectionSplitting import ProjectionSplitter
    from .DirtyLayerRepair import DirtyLayerRepairman

    init_gamera()
except ImportError:
    pass



class DiagonalNeumeSlicing(RodanTask):
    name = 'Diagonal Neume Slicing'
    author = 'Noah Baxter'
    description = 'A tool for splitting neumes into neume components based on diagonal projection.'
    enabled = True
    category = 'Image Processing'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        "job_queue": "Python3",
        'required': ['Smoothing', 'Minimum Glyph Size', 'Maximum Recursive Cuts', 'Angle', 'Minimum Slice Spread', 'Low Valley Threshold', 'Minimum Segment Length', 'Slice Prioritization'],
        'properties': {
            'Smoothing': {
                'type': 'integer',
                'default': 1,
                'minimum': 1,
                'maximum': 20,
                'description': 'How much convolution to apply to projections. More smoothing results in softer cuts.'
            },
            'Minimum Glyph Size': {
                'type': 'integer',
                'default': 0,
                'minimum': 0,
                'maximum': 9999999,
                'description': 'Discard post-splitting glyphs with an x or y dimension less than the Minimum Glyph Size.'
            },
            'Maximum Recursive Cuts': {
                'type': 'integer',
                'default': 10,
                'minimum': 1,
                'maximum': 100,
                'description': 'How many subcuts are allowed on a glyph. Note that this does not equate to the number of cuts, as if no ideal cuts can be found, the image is returned unprocessed.'
            },
            'Angle': {
                'type': 'integer',
                'default': 45,
                'minimum': 0,
                'maximum': 90,
                'description': 'The angle of rotation for finding projections and cutting the image. Best between 30-70 degrees.'
            },
            'Minimum Slice Spread': {
                'type': 'number',
                'default': 0.3,
                'minimum': 0.0,
                'maximum': 1.0,
                'description': 'The minimum spread from valley to peak a slice point must have. Value is a percentage of the maximum projection.'
            },
            'Low Valley Threshold': {
                'type': 'number',
                'default': 1.0,
                'minimum': 0.0,
                'maximum': 1.0,
                'description': 'Forces a cut when a valley lies bellow a percentage of the maximum projection.'
            },
            'Minimum Segment Length': {
                'type': 'integer',
                'default': 5,
                'minimum': 0,
                'maximum': 9999999,
                'description': 'The minimum number of projection values a segment must have. Lower values will allow slice points to be closer together.'
            },
            'Slice Prioritization': {
                'enum': ['None', 'Horizontal', 'Vertical', 'Multi-Cut'],
                'default': 'Vertical',
                'description': 'Prioritize cuts in one dimension over cuts in the other, or picks the overall best slice from both. Horizontal tends to give better results as neumes mostly extend horizontally.'
            },
        },
    }

    input_port_types = [{
        'name': 'GameraXML - Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False,
    }]

    output_port_types = [{
        'name': 'GameraXML - Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False,
    }]

    def run_my_task(self, inputs, settings, outputs):

        glyphs = gamera_xml.glyphs_from_xml(inputs['GameraXML - Connected Components'][0]['resource_path'])

        print (settings)

        kwargs = {
            'smoothing': settings['Smoothing'],
            'extrema_threshold': 0,
            'min_glyph_size': settings['Minimum Glyph Size'],
            'max_recursive_cuts': settings['Maximum Recursive Cuts'],
            'rotation': settings['Angle'],

            # will it cut?
            'min_slice_spread_rel': settings['Minimum Slice Spread'],       # minimum spread for a cut
            'low_projection_threshold': settings['Low Valley Threshold'],   # FORCE a cut if valley under a certain value
            'min_projection_segments': settings['Minimum Segment Length'],  # ++ less likely to cut, -- more slice points

            # Cut prioritizing
            'slice_prioritization': settings['Slice Prioritization'],
            'prefer_multi_cuts': True if settings['Slice Prioritization'] == 'Multi-Cut' else False,
            'prefer_x': True if settings['Slice Prioritization'] == 'Horizontal' else False,
            'prefer_y': True if settings['Slice Prioritization'] == 'Vertical' else False,

            # Try rotated AND non-rotated projections
            'check_axis': False,

            # Debug Options
            'print_projection_array': False,
            'plot_projection_array': False,  # script only
            'save_cuts': False,
        }

        ps = ProjectionSplitter(**kwargs)

        output_glyphs = []
        for g in glyphs:
            output_glyphs += ps.run(g)

        outfile_path = outputs['GameraXML - Connected Components'][0]['resource_path']
        output_xml = gamera_xml.WriteXMLFile(glyphs=output_glyphs,
                                             with_features=True)
        output_xml.write_filename(outfile_path)

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_cc_png_path = "/code/Rodan/rodan/test/files/240r_CC-analysis_output.xml"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/240r_diagonal-neume-slicing_output.xml"
        inputs = {
            "GameraXML - Connected Components": [{"resource_path":input_cc_png_path}]
        }
        outputs = {
            "GameraXML - Connected Components": [{"resource_path":output_path}]
        }
        settings = {'Slice Prioritization': 2, 'Minimum Segment Length': 5, 'Angle': 45, 'Minimum Glyph Size': 0, 'Maximum Recursive Cuts': 10, 'Minimum Slice Spread': 0.3, 'Low Valley Threshold': 1, 'Smoothing': 1} 

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))
        # also each line should be identical to its counterpart
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))


class DirtyLayerRepair(RodanTask):
    name = 'Dirty Layer Repair'
    author = 'Noah Baxter'
    description = 'A tool for \'repairing\' broken layers by adding errors from a dirty layer. For example, using a text layer to repair its neume layer.'
    enabled = True
    category = 'Image Processing'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        "job_queue": "Python3",
        'required': ['Minimum Density', 'Despeckle Size'],
        'properties': {
            'Minimum Density': {
                'type': 'number',
                'default': 0.3,
                'minimum': 0.0,
                'maximum': 1.0,
                'description': 'Use only glyphs with a density less than the maximum from the dirty layer. Smaller values bring more dirt from the dirty layer but may eventually bring undesired glyphs.'
            },
            'Despeckle Size': {
                'type': 'integer',
                'default': 500,
                'minimum': 0,
                'maximum': 1000,
                'description': 'How much post despeckle to apply to the combined output image.'
            }
        }
    }

    input_port_types = [{
        'name': 'Base Layer',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    },
        {
        'name': 'Dirty Layer',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    output_port_types = [{
        'name': 'Repaired Base Layer',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):

        base = load_image(inputs['Base Layer'][0]['resource_path'])
        dirty = load_image(inputs['Dirty Layer'][0]['resource_path'])

        kwargs = {
            'despeckle_size': 500,
            'density': 0.3,
        }

        dlr = DirtyLayerRepairman(**kwargs)
        image = dlr.run(base, dirty)

        outfile_path = outputs['Repaired Base Layer'][0]['resource_path']
        image.save_PNG(outfile_path)

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_base_path = "/code/Rodan/rodan/test/files/ms73-068_neume.png"
        input_dirty_path = "/code/Rodan/rodan/test/files/ms73-068_text.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/ms73-068_dirty-layer-repair.png"
        inputs = {
            "Base Layer": [{"resource_path":input_base_path}],
            "Dirty Layer": [{"resource_path":input_dirty_path}]
        }
        outputs = {
            "Repaired Base Layer": [{"resource_path":output_path}]
        }
        settings = {'Minimum Density': 0.3, 'Despeckle Size': 500} 

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The predicted result and gt result should be identical to each other
        # The gt result is from running this job on production
        gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
        pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        np.testing.assert_array_equal(gt_output, pred_output)
