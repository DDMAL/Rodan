#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/plugins/threshold.py
# Purpose:                Wrapper for threshold plugins.
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

#temporarily moved to run my task while rodan is in python 2 
# import gamera
# from gamera.core import load_image
# from gamera.plugins import threshold
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class gamera_otsu_threshold(RodanTask):

	name = 'Otsu Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.threshold.otsu_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
	settings = {
		'title': 'Otsu threshold settings',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Storage format': {
				'enum': ['Dense (no compression)', 'RLE (run-length encoding compression)'],
				'type': 'string',
				'default': 'Dense (no compression)',
				'description': 'Specifies the compression type for the result.'
			}
		}
	}

	enabled = True
	category = "Gamera - Threshold"
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
		import gamera
		from gamera.core import load_image
		from gamera.plugins import threshold

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.otsu_threshold(settings['Storage format']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

class gamera_tsai_moment_preserving_threshold(RodanTask):

	name = 'Tsai Moment Preserving Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.threshold.tsai_moment_preserving_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
	settings = {
		'title': 'Tsai Moment Preserving Threshold',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Storage format': {
				'enum': ['Dense (no compression)', 'RLE (run-length encoding compression)'],
				'type': 'string',
				'default': 'Dense (no compression)',
				'description': 'Specifies the compression type for the result.'
			}
		}
	}

	enabled = True
	category = "Gamera - Threshold"
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
		import gamera
		from gamera.core import load_image
		from gamera.plugins import threshold

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.tsai_moment_preserving_threshold(settings['Storage format']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

class gamera_abutaleb_threshold(RodanTask):

	name = 'Abutaleb locally-adaptive threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.threshold.abutaleb_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
	settings = {
		'title': 'Abutaleb locally-adaptive threshold',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Storage format': {
				'enum': ['Dense (no compression)', 'RLE (run-length encoding compression)'],
				'type': 'string',
				'default': 'Dense (no compression)',
				'description': 'Specifies the compression type for the result.'
			}
		}
	}

	enabled = True
	category = "Gamera - Threshold"
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
		import gamera
		from gamera.core import load_image
		from gamera.plugins import threshold

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.abutaleb_threshold(settings['Storage format']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

class gamera_bernsen_threshold(RodanTask):

	name = 'Bernsen threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.threshold.bernsen_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
	settings = {
		'title': 'Bernsen threshold',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Storage format': {
				'enum': ['Dense (no compression)', 'RLE (run-length encoding compression)'],
				'type': 'string',
				'default': 'Dense (no compression)',
				'description': 'Specifies the compression type for the result.'
			},
			'Region size': {
				'type': 'integer',
				'minimum': 1,
				'maximum': 50,
				'default': 11,
				'description': 'The size of each region in which to calculate a threshold.'
			},
			'Contrast limit': {
				'type': 'integer',
				'minimum': 0,
				'maximum': 255,
				'default': 80,
				'description': 'The minimum amount of contrast required to threshold.'
			},
			'Doubt to black': {
				'type': 'boolean',
				'default': False,
				'description': 'When True, ''doubtful'' values are set to black, otherwise to white.'
			}
		}
	}

	enabled = True
	category = "Gamera - Threshold"
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
		import gamera
		from gamera.core import load_image
		from gamera.plugins import threshold

		image_source = load_image(inputs['Greyscale PNG image'][0]['resource_path'])
		image_result = image_source.bernsen_threshold(settings['Storage format'], settings['Region size'], settings['Contrast limit'], settings['Doubt to black']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

class gamera_djvu_threshold(RodanTask):

	name = 'DjVu threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.threshold.djvu_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
	settings = {
		'title': 'DjVu threshold',
		'type': 'object',
		'job_queue': 'Python3',
		'properties': {
			'Smoothness': {
				'type': 'number',
				'minimum': 0.0,
				'maximum': 1.0,
				'default': 0.2,
				'description': 'The amount of effect that parent blocks have on their children blocks. Higher values will result in more smoothness between blocks.  Expressed as a percentage between 0.0 and 1.0.'
			},
			'Maximum block size': {
				'type': 'integer',
				'minimum': 1,
				'default': 512,
				'description': 'The size of the largest block to determine a threshold.'
			},
			'Minimum block size': {
				'type': 'integer',
				'minimum': 1,
				'default': 64,
				'description': 'The size of the smallest block to determine a threshold.'
			},
			'Block factor': {
				'type': 'integer',
				'minimum': 1,
				'maximum': 8,
				'default': 2,
				'description': 'The number of child blocks (in each direction) per parent block. For instance, a *block_factor* of 2 results in 4 children per parent.'
			}
		}
	}

	enabled = True
	category = "Gamera - Threshold"
	interactive = False

	input_port_types = [{
		'name': 'RGB PNG image',
		'resource_types': ['image/rgb+png'],
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
		import gamera
		from gamera.core import load_image
		from gamera.plugins import threshold
		
		image_source = load_image(inputs['RGB PNG image'][0]['resource_path'])
		image_result = image_source.djvu_threshold(settings['Smoothness'], settings['Maximum block size'], settings['Minimum block size'], settings['Block factor']) 
		for i in range(len(outputs['Onebit PNG image'])):
			image_result.save_PNG(outputs['Onebit PNG image'][i]['resource_path'])
		return True

