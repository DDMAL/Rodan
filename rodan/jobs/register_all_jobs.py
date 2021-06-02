from rodan.celery import app

# hacky but works
def run_register_jobs():
    try:
        from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier

        app.register_task(InteractiveClassifier())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.interactive_classifier.gamera_xml_distributor import (
            GameraXMLDistributor,
        )

        app.register_task(GameraXMLDistributor())
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

    # TODO: handle "_" imports
    # TODO: complete the python 3 jobs
    # from rodan.jobs.hpc_fast_trainer.hpc_fast_trainer import HPCFastTrainer

    # from rodan.jobs.pil_rodan.red_filtering import RedFilter
    # from rodan.jobs.pil_rodan.resize import resize
    # from rodan.jobs.pil_rodan.to_jpeg2000 import to_jpeg2000
    # from rodan.jobs.pil_rodan.to_png import to_png
    # from rodan.jobs.pil_rodan.to_tiff import to_tiff

    # TODO: GPU jobs
    # from rodan.jobs.Calvo_classifier.calvo_classifier import CalvoClassifier
    # from rodan.jobs.Calvo_classifier.calvo_trainer import CalvoTrainer
    # from rodan.jobs.Calvo_classifier.fast_calvo_classifier import FastCalvoClassifier
    # from rodan.jobs.Calvo_classifier.fast_calvo_trainer import FastCalvoTrainer
    # from rodan.jobs.Calvo_classifier.calvo_trainer import CalvoTrainer

    # from rodan.jobs.text_alignment.text_alignment import text_alignment

    # from rodan.jobs.diagonal_neume_slicing import DiagonalNeumeSlicing
    # from rodan.jobs.diagonal_neume_slicing import DirtyLayerRepair
    # from rodan.jobs.helloworld.helloworld import HelloWorld
    # from rodan.jobs.helloworld.helloworld import HelloWorldMultiPort
    # from rodan.jobs.heuristic_pitch_finding import MiyaoStaffinding
    # from rodan.jobs.heuristic_pitch_finding import HeuristicPitchFinding

    # from rodan.jobs.vis_rodan.wrappers.indexers.cadence_indexer import VRCadenceIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.dissonance_indexer import VRDissonanceIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.duration_indexer import VRDurationIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.fermata_indexer import VRFermataIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.figuredbass_indexer import VRFiguredBassIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.horizontal_interval_indexer import VRHorizontalIntervalIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.measure_indexer import VRMeasureIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.ngram_indexer import VRNGramIntervalIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.notebeatstrength_indexer import VRNoteBeatStrengthIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.noterest_indexer import VRNoteRestIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.offset_indexer import VROffsetIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.vertical_interval_indexer import VRVerticalIntervalIndexer

    # from rodan.jobs.biollante_rodan import BiollanteRodan
    # from rodan.jobs.jSymbolic_Rodan import extract_features
    # from rodan.jobs.neon_wrapper import Neon


if __name__ == "__main__":
    run_register_jobs()
