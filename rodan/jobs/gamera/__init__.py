from gamera.core import init_gamera
init_gamera()

from rodan.jobs import module_loader
from rodan.jobs.gamera.base import load_gamera_module

module_loader('gamera.plugins.binarization', load_gamera_module)
module_loader('gamera.plugins.threshold', load_gamera_module)
module_loader('gamera.plugins.image_conversion', load_gamera_module)
module_loader('gamera.plugins.transformation', load_gamera_module)
module_loader('gamera.toolkits.background_estimation.plugins.background_estimation', load_gamera_module)
module_loader('gamera.toolkits.border_removal.plugins.border_removal', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.border_lyric', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.lyricline', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.lyric_extractor', load_gamera_module)
module_loader('gamera.toolkits.musicstaves.plugins.musicstaves_plugins', load_gamera_module)
module_loader('gamera.toolkits.staffline_removal.plugins.staff_removal', load_gamera_module)

module_loader('rodan.jobs.gamera.tasks.rdn_rotate')
module_loader('rodan.jobs.gamera.custom.border_removal')
module_loader('rodan.jobs.gamera.custom.pixel_segment')
module_loader('rodan.jobs.gamera.custom.pitch_finding.pitch_finding')
module_loader('rodan.jobs.gamera.custom.poly_mask')
module_loader('rodan.jobs.gamera.custom.segmentation.tasks')
module_loader('rodan.jobs.gamera.custom.staff_removal')


####### Toolkits
try:
    from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
    from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
    load_gamera_module(rdn_despeckle)
    load_gamera_module(rdn_despeckle)
    load_gamera_module(rdn_crop)
except ImportError as e:
    logger.warning("The Rodan Plugins have not been installed. Skipping.")
