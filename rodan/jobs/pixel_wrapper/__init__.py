import rodan
__version__ = "1.1.1"
import logging
logger = logging.getLogger('rodan')

from rodan.jobs import module_loader

module_loader('rodan.jobs.pixel_wrapper.wrapper')
