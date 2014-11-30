# [TODO]

import logging
logger = logging.getLogger('rodan')

try:
    from rodan.jobs.neon import module_loader
    module_loader.load_module()
except ImportError as e:
    logger.warning("Custom Pitch Correction job not installed. Skipping. {0}".format(e))
