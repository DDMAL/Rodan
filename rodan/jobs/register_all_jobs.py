from rodan.celery import app

try:
    from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier
    app.register_task(InteractiveClassifier())
except:
    raise ImportError

try:
    from rodan.jobs.resource_distributor import ResourceDistributor
    app.register_task(ResourceDistributor())
except:
    raise ImportError

try:
    from rodan.jobs.helloworld.helloworld import HelloWorld3
    app.register_task(HelloWorld3())
except:
    raise ImportError

try:
    from rodan.jobs.labeler import Labeler
    app.register_task(Labeler())
except:
    raise ImportError

# from rodan.jobs.diagonal-neume-slicing import DiagonalNeumeSlicing
# from rodan.jobs.gamera_rodan import
# from rodan.jobs.helloworld import
# from rodan.jobs.heuristic-pitch-finding import MiyaoStaffinding
try:
    from rodan.jobs.JSOMR2MEI.base import JSOMR2MEI
    app.register_task(JSOMR2MEI())
except:
    raise ImportError

try:
    # from rodan.jobs.jSymbolic-Rodan import extract_features
    from rodan.jobs.MEI_encoding.MEI_encoding import MEI_encoding
    app.register_task(MEI_encoding())
except:
    raise ImportError

try:
    # from rodan.jobs.neon-wrapper import Neon
    from rodan.jobs.pixel_wrapper.wrapper import PixelInteractive
    app.register_task(PixelInteractive())
except:
    raise ImportError

try:
    pass
    # from rodan.jobs.vis-rodan import
    # from rodan.jobs.biollante-rodan import BiollanteRodan
except:
    raise ImportError

try:
    from rodan.jobs.MEI_resizing.mei_resize import MEI_Resize
    app.register_task(MEI_Resize())
except:
    raise ImportError


def run_register_jobs():
    # Python2 jobs
    
    
    # app.register_task(extract_features())
    # app.register_task(MiyaoStaffinding())
    
    # app.register_task(Neon())
    
    
    # app.register_task(DiagonalNeumeSlicing())
    # app.register_task(BiollanteRodan())

    # Python3 jobs
    

    # Core jobs
    pass
    
    
if __name__ == "__main__":
    run_register_jobs()
