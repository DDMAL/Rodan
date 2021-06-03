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

    try:
        from rodan.jobs.hpc_fast_trainer.hpc_fast_trainer import HPCFastTrainer

        app.register_task(HPCFastTrainer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pil_rodan.red_filtering import RedFilter

        app.register_task(RedFilter())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pil_rodan.resize import resize

        app.register_task(resize())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pil_rodan.to_jpeg2000 import to_jpeg2000

        app.register_task(to_jpeg2000())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pil_rodan.to_png import to_png

        app.register_task(to_png())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.pil_rodan.to_tiff import to_tiff

        app.register_task(to_tiff())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.Calvo_classifier.calvo_classifier import CalvoClassifier

        app.register_task(CalvoClassifier())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.Calvo_classifier.calvo_trainer import CalvoTrainer

        app.register_task(CalvoTrainer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.Calvo_classifier.fast_calvo_classifier import (
            FastCalvoClassifier,
        )

        app.register_task(FastCalvoClassifier())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.Calvo_classifier.fast_calvo_trainer import FastCalvoTrainer

        app.register_task(FastCalvoTrainer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.text_alignment.text_alignment import text_alignment

        app.register_task(text_alignment())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.diagonal_neume_slicing import DiagonalNeumeSlicing

        app.register_task(DiagonalNeumeSlicing())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.diagonal_neume_slicing import DirtyLayerRepair

        app.register_task(DirtyLayerRepair())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.heuristic_pitch_finding import MiyaoStaffinding

        app.register_task(MiyaoStaffinding())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.heuristic_pitch_finding import HeuristicPitchFinding

        app.register_task(HeuristicPitchFinding())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.cadence_indexer import VRCadenceIndexer
        app.register_task(VRCadenceIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.dissonance_indexer import VRDissonanceIndexer
        app.register_task(VRDissonanceIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.duration_indexer import VRDurationIndexer
        app.register_task(VRDurationIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.fermata_indexer import VRFermataIndexer
        app.register_task(VRFermataIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.figuredbass_indexer import VRFiguredBassIndexer
        app.register_task(VRFiguredBassIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.horizontal_interval_indexer import VRHorizontalIntervalIndexer
        app.register_task(VRHorizontalIntervalIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.measure_indexer import VRMeasureIndexer
        app.register_task(VRMeasureIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.ngram_indexer import VRNGramIntervalIndexer
        app.register_task(VRNGramIntervalIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)
    
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.notebeatstrength_indexer import VRNoteBeatStrengthIndexer
        app.register_task(VRNoteBeatStrengthIndexer())
    except ImportError as error:
        print(error.__class__.__name__ + ": " + error.message)


    # TODO: GPU jobs
    # from rodan.jobs.helloworld.helloworld import HelloWorld -- i'll leave this commented out 
    # from rodan.jobs.helloworld.helloworld import HelloWorldMultiPort
    # from rodan.jobs.helloworld.helloworld import HelloWorld3

    # from rodan.jobs.vis_rodan.wrappers.indexers.noterest_indexer import VRNoteRestIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.offset_indexer import VROffsetIndexer
    # from rodan.jobs.vis_rodan.wrappers.indexers.vertical_interval_indexer import VRVerticalIntervalIndexer

    # from rodan.jobs.biollante_rodan import BiollanteRodan
    # from rodan.jobs.jSymbolic_Rodan import extract_features
    # from rodan.jobs.neon_wrapper import Neon


if __name__ == "__main__":
    run_register_jobs()
