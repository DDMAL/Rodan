import logging

import rodan
from rodan.jobs import module_loader

__version__ = "0.0.2"
logger = logging.getLogger("rodan")
module_loader("rodan.jobs.aquitanian_staff_detection.aquitanian_staff_detection")
