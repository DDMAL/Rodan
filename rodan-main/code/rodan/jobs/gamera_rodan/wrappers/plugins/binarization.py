#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/plugins/binarization.py
# Purpose:                Wrapper for binarization plugins.
#
# Copyright (C) 2016 DDMAL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

try:
	import gamera
	from gamera.core import load_image
	from gamera.plugins import binarization
except ImportError:
	pass

from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class gamera_gatos_background(RodanTask):

	name = 'Gatos Background'
	author = 'Ryan Bannon'
	description = """
    Estimates the background of an image according to Gatos et al.'s
    method. See:

    Gatos, Basilios, Ioannis Pratikakis, and Stavros
    J. Perantonis. 2004. An adaptive binarization technique for low
    quality historical documents. *Lecture Notes in Computer
    Science* 3163: 102--113.

    *region_size* 
      Region size for interpolation.

    *binarization*
      A preliminary binarization of the image.
    """
	settings ={
		'title': 'Gatos background settings',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Region size': {
			'type': 'integer',
			'minimum': 1,
			'default': 15
			}	
	   }
	}

	enabled = True
	category = 'Gamera - Binarization'
	interactive = False

	input_port_types = [{
		'name': 'Onebit PNG - preliminary binarization of the image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 1
	},
	{
		'name': 'Greyscale PNG - source image to binarize',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	}]
	output_port_types = [{
		'name': 'Greyscale PNG - background estimation image',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 2
	}]

	def run_my_task(self, inputs, settings, outputs):

		image_source = load_image(inputs['Greyscale PNG - source image to binarize'][0]['resource_path'])
		image_prelim = load_image(inputs['Onebit PNG - preliminary binarization of the image'][0]['resource_path'])
		image_result = image_source.gatos_background(image_prelim, settings['Region size'])
		for i in range(len(outputs['Greyscale PNG - background estimation image'])):
			image_result.save_PNG(outputs['Greyscale PNG - background estimation image'][i]['resource_path'])
		return True

	def test_my_task(self, testcase):
		import cv2
		import numpy as np
		input_onebit_png_path = "/code/Rodan/rodan/test/files/CF-005_one-bit-png_output.png"
		input_greyscale_png_path = "/code/Rodan/rodan/test/files/CF-005_greyscale-png_output.png"
		output_path = testcase.new_available_path()
		gt_output_path = "/code/Rodan/rodan/test/files/CF-005_gatos-background_output.png"

		inputs = {
			"Onebit PNG - preliminary binarization of the image": [{"resource_path":input_onebit_png_path}],
			"Greyscale PNG - source image to binarize": [{"resource_path":input_greyscale_png_path}]
		}
		outputs = {
			"Greyscale PNG - background estimation image": [{"resource_path":output_path}]
		}
		settings = {
			"Region size":15
		}

		self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

		# The predicted result and gt result should be identical to each other
		# The gt result is from running this job (gatos background) on production
		gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
		pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

		np.testing.assert_array_equal(gt_output, pred_output)

class gamera_gatos_threshold(RodanTask):

	name = 'Gatos Threshold'
	author = 'Ryan Bannon'
	description = """
    Thresholds an image according to Gatos et al.'s method. See:

    Gatos, Basilios, Ioannis Pratikakis, and Stavros
    J. Perantonis. 2004. An adaptive binarization technique for low
    quality historical documents. *Lecture Notes in Computer
    Science* 3163: 102-113.

    *background*
      Estimated background of the image.

    *binarization*
      A preliminary binarization of the image.

    Use the default settings for the other parameters unless you know
    what you are doing.
    """
	settings = {
		'title': 'Gatos threshold settings',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'q': {
				'type': 'number',
				'default': 0.6,
				'description': 'Use default setting (unless you know what you are doing).'
			},
			'p1': {
				'type': 'number',
				'default': 0.5,
				'description': 'Use default setting (unless you know what you are doing).' 
			},
			'p2': {
				'type': 'number',
				'default': 0.8,
				'description': 'Use default setting (unless you know what you are doing).'
			}
		}
	}

	enabled = True
	category = "Gamera - Binarization"
	interactive = False

	input_port_types = [{
		'name': 'Onebit PNG - preliminary binarization of the image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 1
	},
	{
		'name': 'Greyscale PNG - estimated background of the image',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	},
	{
		'name': 'Greyscale PNG - source image to binarize',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	}]
	output_port_types = [{
		'name': 'Onebit PNG image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 2
	}]

	def run_my_task(self, inputs, settings, outputs):

		image_source = load_image(inputs['Greyscale PNG - source image to binarize'][0]['resource_path'])
		image_background = load_image(inputs['Greyscale PNG - estimated background of the image'][0]['resource_path'])
		image_prelim = load_image(inputs['Onebit PNG - preliminary binarization of the image'][0]['resource_path'])
		image_result = image_source.gatos_threshold(image_background, image_prelim, settings['q'], settings['p1'], settings['p2']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

	def test_my_task(self, testcase):
		import cv2
		import numpy as np
		input_onebit_png_path = "/code/Rodan/rodan/test/files/CF-005_one-bit-png_output.png"
		input_background_png_path =  "/code/Rodan/rodan/test/files/CF-005_gatos-background_output.png"
		input_greyscale_png_path = "/code/Rodan/rodan/test/files/CF-005_greyscale-png_output.png"
		output_path = testcase.new_available_path()
		gt_output_path = "/code/Rodan/rodan/test/files/CF-005_gatos-threshold_output.png"
		inputs = {
			"Onebit PNG - preliminary binarization of the image": [{"resource_path":input_onebit_png_path}],
			"Greyscale PNG - estimated background of the image": [{"resource_path":input_background_png_path}],
			"Greyscale PNG - source image to binarize": [{"resource_path":input_greyscale_png_path}]
		}
		outputs = {
			"Onebit PNG image": [{"resource_path":output_path}]
		}
		settings = {
			"q":0.6,
			"p1": 0.5,
			"p2": 0.8
		}

		self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

		# The predicted result and gt result should be identical to each other
		# The gt result is from running this job (gatos threshold) on production
		gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
		pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

		np.testing.assert_array_equal(gt_output, pred_output)

class gamera_brink_threshold(RodanTask):

	name = 'Brink Threshold'
	author = 'Ryan Bannon'
	description = """
    Calculates threshold for image with Brink and Pendock's minimum-cross    
    entropy method and returns corrected image. It is best used for binarising
    images with dark, near-black foreground and significant bleed-through.
    To that end, it generally predicts lower thresholds than other
    thresholding algorithms.

    Reference: A.D. Brink, N.E. Pendock: Minimum cross-entropy threshold selection.
    Pattern Recognition 29 (1), 1996. 179-188.
    """
	settings = {'job_queue': 'Python3'}

	enabled = True
	category = "Gamera - Binarization"
	interactive = False

	input_port_types = [{
		'name': 'Greyscale PNG image',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	}]
	output_port_types = [{
		'name': 'Onebit PNG image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 2
	}]

	def run_my_task(self, inputs, settings, outputs):

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.brink_threshold() 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

	def test_my_task(self, testcase):
		import cv2
		import numpy as np
		input_greyscale_png_path = "/code/Rodan/rodan/test/files/CF-005_greyscale-png_output.png"
		output_path = testcase.new_available_path()
		gt_output_path = "/code/Rodan/rodan/test/files/CF-005_brink-threshold_output.png"
		inputs = {
			"Greyscale PNG image": [{"resource_path":input_greyscale_png_path}]
		}
		outputs = {
			"Onebit PNG image": [{"resource_path":output_path}]
		}
		settings = {
		}

		self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

		# The predicted result and gt result should be identical to each other
		# The gt result is from running this job (blink threshold) on production
		gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
		pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

		np.testing.assert_array_equal(gt_output, pred_output)

class gamera_sauvola_threshold(RodanTask):

	name = 'Sauvola Threshold'
	author = 'Ryan Bannon'
	description = """
    Creates a binary image using Sauvola's adaptive algorithm.

    Sauvola, J. and M. Pietikainen. 2000. Adaptive document image
    binarization.  *Pattern Recognition* 33: 225--236.

    Like the QGAR library, there are two extra global thresholds for
    the lightest and darkest regions.

    *region_size*
      The size of the region in which to calculate a threshold.

    *sensitivity*
      The sensitivity weight on the adjusted variance.

    *dynamic_range*
      The dynamic range of the variance.

    *lower bound*
      A global threshold beneath which all pixels are considered black.

    *upper bound*
      A global threshold above which all pixels are considered white.
    """
	settings = {
		'title': 'Sauvola threshold settings',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Region size': {
				'type': 'integer',
				'default': 15,
				'description': 'The size of the region in which to calculate a threshold.'
			},
			'Sensitivity': {
				'type': 'number',
				'default': 0.5,
				'description': 'The sensitivity weight on the adjusted variance.' 
			},
			'Dynamic range': {
				'type': 'integer',
				'minimum': 1,
				'maximum': 255,
				'default': 128,
				'description': 'The dynamic range of the variance.'
			},
			'Lower bound': {
				'type': 'integer',
				'minimum': 0,
				'maximum': 255,
				'default': 20,
				'description': 'A global threshold beneath which all pixels are considered black.'
			},
			'Upper bound': {
				'type': 'integer',
				'minimum': 0,
				'maximum': 255,
				'default': 150,
				'description': 'A global threshold above which all pixels are considered white.'
			}
		}
	}

	enabled = True
	category = "Gamera - Binarization"
	interactive = False

	input_port_types = [{
		'name': 'Greyscale PNG image',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	}]
	output_port_types = [{
		'name': 'Onebit PNG image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 2
	}]

	def run_my_task(self, inputs, settings, outputs):

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.sauvola_threshold(settings['Region size'], settings['Sensitivity'], settings['Dynamic range'], settings['Lower bound'], settings['Upper bound']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

	def test_my_task(self, testcase):
		import cv2
		import numpy as np
		input_greyscale_png_path = "/code/Rodan/rodan/test/files/CF-005_greyscale-png_output.png"
		output_path = testcase.new_available_path()
		gt_output_path = "/code/Rodan/rodan/test/files/CF-005_sauvola-threshold_output.png"
		inputs = {
			"Greyscale PNG image": [{"resource_path":input_greyscale_png_path}]
		}
		outputs = {
			"Onebit PNG image": [{"resource_path":output_path}]
		}
		settings = {
			'Region size': 15,
			'Sensitivity': 0.5,
			'Dynamic range': 128,
			'Lower bound': 20,
			'Upper bound': 150
		}

		self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

		# The predicted result and gt result should be identical to each other
		# The gt result is from running this job (sauvola threshold) on production
		gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
		pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

		np.testing.assert_array_equal(gt_output, pred_output)

class gamera_niblack_threshold(RodanTask):

	name = 'Niblack Threshold'
	author = 'Ryan Bannon'
	description = """
    Creates a binary image using Niblack's adaptive algorithm.

    Niblack, W. 1986. *An Introduction to Digital Image Processing.* Englewood
    Cliffs, NJ: Prentice Hall.

    Like the QGAR library, there are two extra global thresholds for
    the lightest and darkest regions.

    *region_size*
      The size of the region in which to calculate a threshold.

    *sensitivity*
      The sensitivity weight on the variance.

    *lower bound*
      A global threshold beneath which all pixels are considered black.

    *upper bound*
      A global threshold above which all pixels are considered white.
    """
	settings = {
		'title': 'Niblack threshold settings',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Region size': {
				'type': 'integer',
				'default': 15,
				'description': 'The size of the region in which to calculate a threshold.'
			},
			'Sensitivity': {
				'type': 'number',
				'default': -0.2,
				'description': 'The sensitivity weight on the adjusted variance.' 
			},
			'Lower bound': {
				'type': 'integer',
				'minimum': 0,
				'maximum': 255,
				'default': 20,
				'description': 'A global threshold beneath which all pixels are considered black.'
			},
			'Upper bound': {
				'type': 'integer',
				'minimum': 0,
				'maximum': 255,
				'default': 150,
				'description': 'A global threshold above which all pixels are considered white.'
			}
		}
	}

	enabled = True
	category = "Gamera - Binarization"
	interactive = False

	input_port_types = [{
		'name': 'Greyscale PNG image',
		'resource_types': ['image/greyscale+png'],
		'minimum': 1,
		'maximum': 1
	}]
	output_port_types = [{
		'name': 'Onebit PNG image',
		'resource_types': ['image/onebit+png'],
		'minimum': 1,
		'maximum': 2
	}]

	def run_my_task(self, inputs, settings, outputs):

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.niblack_threshold(settings['Region size'], settings['Sensitivity'], settings['Lower bound'], settings['Upper bound']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

	def test_my_task(self, testcase):
		import cv2
		import numpy as np
		input_greyscale_png_path = "/code/Rodan/rodan/test/files/CF-005_greyscale-png_output.png"
		output_path = testcase.new_available_path()
		gt_output_path = "/code/Rodan/rodan/test/files/CF-005_niblack-threshold_output.png"
		inputs = {
			"Greyscale PNG image": [{"resource_path":input_greyscale_png_path}]
		}
		outputs = {
			"Onebit PNG image": [{"resource_path":output_path}]
		}
		settings = {
			'Region size': 15,
			'Sensitivity': -0.2,
			'Lower bound': 20,
			'Upper bound': 150
		}

		self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

		# The predicted result and gt result should be identical to each other
		# The gt result is from running this job (niblack threshold) on production
		gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
		pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

		np.testing.assert_array_equal(gt_output, pred_output)