import logging, importlib
logger = logging.getLogger('rodan')

def module_loader(name, callback=lambda m: None, raise_exception=False):
    try:
        logger.info("Importing: " + name)
        m = importlib.import_module(name)
        callback(m)
    except ImportError as e:
        if not raise_exception:
            logger.warning("Trouble loading module {0}. Message: {1}".format(name, e))
        else:
            raise ImportError("Trouble loading module {0}. Message: {1}".format(name, e))

package_versions = {}
