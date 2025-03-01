import logging

import rodan
from rodan.jobs import module_loader

__version__ = "0.0.2"
logger = logging.getLogger("rodan")
module_loader("rodan.jobs.one_staff_finding.one_staff_finding")
