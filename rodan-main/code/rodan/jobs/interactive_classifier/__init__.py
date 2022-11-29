__version__ = "1.0.0"
#from .gamera_xml_distributor import GameraXMLDistributor
#from .wrapper import InteractiveClassifier

from rodan.jobs import module_loader
module_loader("rodan.jobs.interactive_classifier.gamera_xml_distributor")
module_loader("rodan.jobs.interactive_classifier.wrapper")