import rodan
__version__ = "1.2.3"

import logging
logger = logging.getLogger('rodan')

from rodan.jobs import module_loader

module_loader('rodan.jobs.Calvo_classifier.calvo_classifier')
module_loader('rodan.jobs.Calvo_classifier.calvo_trainer')
module_loader('rodan.jobs.Calvo_classifier.fast_calvo_classifier')
module_loader('rodan.jobs.Calvo_classifier.fast_calvo_trainer')
