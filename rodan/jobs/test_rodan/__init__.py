import logging

import rodan  # noqa
from rodan.jobs import module_loader

__version__ = "0.0.1"
logger = logging.getLogger("rodan")
module_loader("rodan.jobs.test_rodan.test_rodan")