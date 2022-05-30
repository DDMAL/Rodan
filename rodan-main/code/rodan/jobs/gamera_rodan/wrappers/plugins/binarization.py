#!/usr/bin/env python
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

import gamera
from gamera.core import load_image
from gamera.plugins import binarization
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class gamera_gatos_background(RodanTask):

	name = 'Gatos Background'
	author = 'Ryan Bannon'
	description = binarization.gatos_background.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
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

class gamera_gatos_threshold(RodanTask):

	name = 'Gatos Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.binarization.gatos_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
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

class gamera_brink_threshold(RodanTask):

	name = 'Brink Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.binarization.brink_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
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

class gamera_sauvola_threshold(RodanTask):

	name = 'Sauvola Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.binarization.sauvola_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
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

class gamera_niblack_threshold(RodanTask):

	name = 'Niblack Threshold'
	author = 'Ryan Bannon'
	description = gamera.plugins.binarization.niblack_threshold.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
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
