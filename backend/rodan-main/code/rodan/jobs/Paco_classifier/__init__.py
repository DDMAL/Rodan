import rodan
__version__ = "1.2.3"

import logging
logger = logging.getLogger('rodan')

from rodan.jobs import module_loader

module_loader('rodan.jobs.Paco_classifier.fast_paco_classifier')
module_loader('rodan.jobs.Paco_classifier.fast_paco_trainer')
