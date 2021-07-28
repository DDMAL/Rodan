import rodan
__version__ = "1.0.0"
import logging

logger = logging.getLogger("rodan")
from rodan.jobs import module_loader
module_loader("rodan.jobs.MEI_encoding.MEI_encoding")
