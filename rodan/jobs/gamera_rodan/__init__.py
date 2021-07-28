__version__ = "0.1.0"

from gamera.core import init_gamera
init_gamera()
from rodan.jobs import module_loader

module_loader('rodan.jobs.gamera_rodan.wrappers.classification')
module_loader('rodan.jobs.gamera_rodan.wrappers.masking')

module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.binarization')
module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.cc_analysis')
module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.image_conversion')
module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.morphology')
module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.threshold')
module_loader('rodan.jobs.gamera_rodan.wrappers.plugins.image_utilities')

module_loader('rodan.jobs.gamera_rodan.wrappers.toolkits.music_staves.miyao')
module_loader('rodan.jobs.gamera_rodan.wrappers.toolkits.music_staves.roach_tatem')
module_loader('rodan.jobs.gamera_rodan.wrappers.toolkits.document_preprocessing_toolkit.stable_paths')
module_loader('rodan.jobs.gamera_rodan.wrappers.toolkits.custom.poly_mask')
