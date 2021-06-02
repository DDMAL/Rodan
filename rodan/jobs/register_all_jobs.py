from rodan.celery import app

try:
    from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier
    from rodan.jobs.resource_distributor import ResourceDistributor
    from rodan.jobs.helloworld.helloworld import HelloWorld3
    from rodan.jobs.labeler import Labeler
    

    # from rodan.jobs.diagonal-neume-slicing import DiagonalNeumeSlicing
    # from rodan.jobs.gamera_rodan import
    # from rodan.jobs.helloworld import
    # from rodan.jobs.heuristic-pitch-finding import MiyaoStaffinding
    # rom rodan.jobs.JSOMR2MEI.base import JSOMR2MEI

    # from rodan.jobs.jSymbolic-Rodan import extract_features
    # from rodan.jobs.MEI_encoding.MEI_encoding import MEI_encoding

    # from rodan.jobs.neon-wrapper import Neon
    # from rodan.jobs.pixel_wrapper import PixelInteractive

    # from rodan.jobs.vis-rodan import
    # from rodan.jobs.biollante-rodan import BiollanteRodan
    # from rodan.jobs.MEI_resizing.mei_resizing import MEI_Resize
except (ImportError):
    raise ImportError(
        "Problem importing jobs, make sure imports are configured correctly"
    )


def run_register_jobs():
    # Python2 jobs
    app.register_task(InteractiveClassifier())
    # app.register_task(JSOMR2MEI())
    # app.register_task(extract_features())
    # app.register_task(MiyaoStaffinding())
    # app.register_task(MEI_encoding())
    # app.register_task(Neon())
    # app.register_task(PixelInteractive())
    # app.register_task(MEI_Resize())
    # app.register_task(DiagonalNeumeSlicing())
    # app.register_task(BiollanteRodan())

    # Python3 jobs
    app.register_task(HelloWorld3())

    # Core jobs
    app.register_task(ResourceDistributor())
    app.register_task(Labeler())


if __name__ == "__main__":
    run_register_jobs()
