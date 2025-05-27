import rodan
from rodan.jobs import module_loader
import logging

__version__ = "0.0.1"
logger = logging.getLogger('rodan')
module_loader('rodan.jobs.mei2vol_wrapper.m2v_wrapper')
