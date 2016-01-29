import logging, importlib
logger = logging.getLogger('rodan')

def module_loader(name, callback=lambda m: None):
    try:
        logger.info("Importing: " + name)
        m = importlib.import_module(name)
        callback(m)
    except ImportError as e:
        raise ImportError("Trouble loading module {0}.\nMessage: {1}".format(name, e))

package_versions = {}
