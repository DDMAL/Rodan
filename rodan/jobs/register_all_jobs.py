from rodan.celery import app

# hacky but works
def run_register_jobs():
    try:
        from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier

        app.register_task(InteractiveClassifier())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.resource_distributor import ResourceDistributor

        app.register_task(ResourceDistributor())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.helloworld.helloworld import HelloWorld3

        app.register_task(HelloWorld3())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.labeler import Labeler

        app.register_task(Labeler())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.JSOMR2MEI.base import JSOMR2MEI

        app.register_task(JSOMR2MEI())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.MEI_encoding.MEI_encoding import MEI_encoding

        app.register_task(MEI_encoding())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pixel_wrapper.wrapper import PixelInteractive

        app.register_task(PixelInteractive())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.MEI_resizing.mei_resize import MEI_Resize

        app.register_task(MEI_Resize())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.gamera_rodan.wrappers.classification import ClassificationTask

        app.register_task(ClassificationTask())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalAnd

        app.register_task(GameraMaskLogicalAnd())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalXor

        app.register_task(GameraMaskLogicalXor())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    # TODO: handle "-" imports
    # TODO: complete the python 3 jobs
    # from rodan.jobs.hpc-fast-trainer.hpc-fast-trainer import HPCFastTrainer

    # from rodan.jobs.pil-rodan.red_filtering import RedFilter
    # from rodan.jobs.pil-rodan.resize import resize
    # from rodan.jobs.pil-rodan.to_jpeg2000 import to_jpeg2000
    # from rodan.jobs.pil-rodan.to_png import to_png
    # from rodan.jobs.pil-rodan.to_tiff import to_tiff

    # TODO: GPU jobs
    # from rodan.jobs.Calvo-classifier import
    # from rodan.jobs.text_alignment import

    # from rodan.jobs.diagonal-neume-slicing import DiagonalNeumeSlicing
    # from rodan.jobs.diagonal-neume-slicing import DirtyLayerRepair
    # from rodan.jobs.helloworld.helloworld import HelloWorld
    # from rodan.jobs.helloworld.helloworld import HelloWorldMultiPort
    # from rodan.jobs.heuristic-pitch-finding import MiyaoStaffinding

    # from rodan.jobs.vis-rodan.wrappers.indexers.cadence_indexer import VRCadenceIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.dissonance_indexer import VRDissonanceIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.duration_indexer import VRDurationIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.fermata_indexer import VRFermataIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.figuredbass_indexer import VRFiguredBassIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.horizontal_interval_indexer import VRHorizontalIntervalIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.measure_indexer import VRMeasureIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.ngram_indexer import VRNGramIntervalIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.notebeatstrength_indexer import VRNoteBeatStrengthIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.noterest_indexer import VRNoteRestIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.offset_indexer import VROffsetIndexer
    # from rodan.jobs.vis-rodan.wrappers.indexers.vertical_interval_indexer import VRVerticalIntervalIndexer

    # from rodan.jobs.biollante-rodan import BiollanteRodan
    # from rodan.jobs.jSymbolic-Rodan import extract_features
    # from rodan.jobs.neon-wrapper import Neon


if __name__ == "__main__":
    run_register_jobs()
