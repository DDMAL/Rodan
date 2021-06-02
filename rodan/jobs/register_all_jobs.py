from rodan.celery import app


def run_register_jobs():
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
        from rodan.jobs.MEI_resizing.mei_resize import MEI_Resize

        app.register_task(MEI_Resize())
    except:
        raise ImportError

    try:
        from rodan.jobs.gamera_rodan.wrappers.classification import ClassificationTask

        app.register_task(ClassificationTask())
        from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalAnd

        app.register_task(GameraMaskLogicalAnd())
    except:
        raise ImportError

    # TODO: handle "-" imports
    # TODO: conplete the python 3 jobs
    # from rodan.jobs.helloworld"
    # from rodan.jobs.hpc-fast-trainer"
    # from rodan.jobs.pil-rodan"

    # from rodan.jobs.diagonal-neume-slicing import DiagonalNeumeSlicing
    # from rodan.jobs.helloworld import
    # from rodan.jobs.heuristic-pitch-finding import MiyaoStaffinding
    # from rodan.jobs.vis-rodan import
    # from rodan.jobs.biollante-rodan import BiollanteRodan


if __name__ == "__main__":
    run_register_jobs()
