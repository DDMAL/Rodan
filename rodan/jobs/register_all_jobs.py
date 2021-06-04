from rodan.celery import app

"""
Script for registering Rodan jobs with Celery, split into their respective queues
"""


# Register all jobs
def register_all():

    # Register all jobs
    register_base()
    register_py2()
    register_py3()
    register_gpu()


# base jobs
def register_base():

    # Register Resource Distributor
    try:
        from rodan.jobs.resource_distributor import ResourceDistributor

        app.register_task(ResourceDistributor())
    except ImportError:
        pass

    # Register Labeler
    try:
        from rodan.jobs.labeler import Labeler

        app.register_task(Labeler())
    except ImportError:
        pass


# Python2 Jobs
def register_py2():

    # Register IC
    try:
        from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier

        app.register_task(InteractiveClassifier())
    except ImportError:
        pass

    try:
        from rodan.jobs.interactive_classifier.gamera_xml_distributor import (
            GameraXMLDistributor,
        )

        app.register_task(GameraXMLDistributor())
    except ImportError:
        pass

    # Register JSOMR2MEI
    try:
        from rodan.jobs.JSOMR2MEI.base import JSOMR2MEI

        app.register_task(JSOMR2MEI())
    except ImportError:
        pass

    # Register MEI Encoding
    try:
        from rodan.jobs.MEI_encoding.MEI_encoding import MEI_encoding

        app.register_task(MEI_encoding())
    except ImportError:
        pass

    # Register Pixel.js
    try:
        from rodan.jobs.pixel_wrapper.wrapper import PixelInteractive

        app.register_task(PixelInteractive())
    except ImportError:
        pass

    # Register MEI resizing
    try:
        from rodan.jobs.MEI_resizing.mei_resize import MEI_Resize

        app.register_task(MEI_Resize())
    except ImportError:
        pass

    # Register Gamera
    try:
        from rodan.jobs.gamera_rodan.wrappers.classification import ClassificationTask

        app.register_task(ClassificationTask())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.binarization import (
            gamera_gatos_background,
        )

        app.register_task(gamera_gatos_background())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.binarization import (
            gamera_gatos_threshold,
        )

        app.register_task(gamera_gatos_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.binarization import (
            gamera_brink_threshold,
        )

        app.register_task(gamera_brink_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.binarization import (
            gamera_sauvola_threshold,
        )

        app.register_task(gamera_sauvola_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.binarization import (
            gamera_niblack_threshold,
        )

        app.register_task(gamera_niblack_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.cc_analysis import (
            CCAnalysis,
        )

        app.register_task(CCAnalysis())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.image_conversion import (
            gamera_to_rgb,
        )

        app.register_task(gamera_to_rgb())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.image_conversion import (
            gamera_to_greyscale,
        )

        app.register_task(gamera_to_greyscale())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.image_conversion import (
            gamera_to_grey16,
        )

        app.register_task(gamera_to_grey16())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.image_conversion import (
            gamera_to_onebit,
        )

        app.register_task(gamera_to_onebit())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.image_utilities import (
            gamera_invert,
        )

        app.register_task(gamera_invert())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.morphology import (
            gamera_despeckle,
        )

        app.register_task(gamera_despeckle())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.morphology import (
            gamera_dilate,
        )

        app.register_task(gamera_dilate())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.threshold import (
            gamera_otsu_threshold,
        )

        app.register_task(gamera_otsu_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.threshold import (
            gamera_tsai_moment_preserving_threshold,
        )

        app.register_task(gamera_tsai_moment_preserving_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.threshold import (
            gamera_abutaleb_threshold,
        )

        app.register_task(gamera_abutaleb_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.threshold import (
            gamera_bernsen_threshold,
        )

        app.register_task(gamera_bernsen_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.pluggins.threshold import (
            gamera_djvu_threshold,
        )

        app.register_task(gamera_djvu_threshold())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.toolkits.custom.poly_mask import (
            PolyMask,
        )

        app.register_task(PolyMask())
    except ImportError:
        pass

    # try:
    #     from rodan.jobs.gamera_rodan.wrappers.toolkits.document-preprocessing-toolkit.stable_paths import ( # noqa
    #         StablePaths,
    #     )

    #     app.register_task(StablePaths())
    # except ImportError:
    #     pass

    # try:
    #     from rodan.jobs.gamera_rodan.wrappers.toolkits.document-preprocessing-toolkit.stable_paths import ( # noqa
    #         StablePathDetection,
    #     )

    #     app.register_task(StablePathDetection())
    # except ImportError:
    #     pass

    # try:
    #     from rodan.jobs.gamera_rodan.wrappers.toolkits.music-staves.miyao import (
    #         MiyaoStaffFinder,
    #     )

    #     app.register_task(MiyaoStaffFinder())
    # except ImportError:
    #     pass

    # try:
    #     from rodan.jobs.gamera_rodan.wrappers.toolkits.music-staves.roach_tatem import (
    #         RoachTatemRemoveStaffLines,
    #     )

    #     app.register_task(RoachTatemRemoveStaffLines())
    # except ImportError:
    #     pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalAnd

        app.register_task(GameraMaskLogicalAnd())
    except ImportError:
        pass

    try:
        from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalXor

        app.register_task(GameraMaskLogicalXor())
    except ImportError:
        pass

    # Register Neume Slicing
    try:
        from rodan.jobs.diagonal_neume_slicing import DiagonalNeumeSlicing

        app.register_task(DiagonalNeumeSlicing())
    except ImportError:
        pass

    try:
        from rodan.jobs.diagonal_neume_slicing import DirtyLayerRepair

        app.register_task(DirtyLayerRepair())
    except ImportError:
        pass

    # Register HPF
    try:
        from rodan.jobs.heuristic_pitch_finding import MiyaoStaffinding

        app.register_task(MiyaoStaffinding())
    except ImportError:
        pass

    try:
        from rodan.jobs.heuristic_pitch_finding import HeuristicPitchFinding

        app.register_task(HeuristicPitchFinding())
    except ImportError:
        pass

    # Register VIS
    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.cadence_indexer import (
            VRCadenceIndexer,
        )

        app.register_task(VRCadenceIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.dissonance_indexer import (
            VRDissonanceIndexer,
        )

        app.register_task(VRDissonanceIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.duration_indexer import (
            VRDurationIndexer,
        )

        app.register_task(VRDurationIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.fermata_indexer import (
            VRFermataIndexer,
        )

        app.register_task(VRFermataIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.figuredbass_indexer import (
            VRFiguredBassIndexer,
        )

        app.register_task(VRFiguredBassIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.horizontal_interval_indexer import (
            VRHorizontalIntervalIndexer,
        )

        app.register_task(VRHorizontalIntervalIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.measure_indexer import (
            VRMeasureIndexer,
        )

        app.register_task(VRMeasureIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.ngram_indexer import (
            VRNGramIntervalIndexer,
        )

        app.register_task(VRNGramIntervalIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.notebeatstrength_indexer import (
            VRNoteBeatStrengthIndexer,
        )

        app.register_task(VRNoteBeatStrengthIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.noterest_indexer import (
            VRNoteRestIndexer,
        )

        app.register_task(VRNoteRestIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.offset_indexer import (
            VROffsetIndexer,
        )

        app.register_task(VROffsetIndexer())
    except ImportError:
        pass

    try:
        from rodan.jobs.vis_rodan.wrappers.indexers.vertical_interval_indexer import (
            VRVerticalIntervalIndexer,
        )

        app.register_task(VRVerticalIntervalIndexer())
    except ImportError:
        pass

    # Register Biollante
    try:
        from rodan.jobs.biollante_rodan import BiollanteRodan

        app.register_task(BiollanteRodan())
    except ImportError:
        pass

    # Register jSymbolic
    try:
        from rodan.jobs.jSymbolic_Rodan.extract_features import extract_features

        app.register_task(extract_features())
    except ImportError:
        pass

    # Register Neon
    try:
        from rodan.jobs.neon_wrapper.wrapper import Neon

        app.register_task(Neon())
    except ImportError:
        pass


# Python3 Jobs
def register_py3():

    # Register Hello World
    try:
        from rodan.jobs.helloworld.helloworld import HelloWorld

        app.register_task(HelloWorld())
    except ImportError:
        pass

    try:
        from rodan.jobs.helloworld.helloworld import HelloWorldMultiPort

        app.register_task(HelloWorldMultiPort())
    except ImportError:
        pass

    try:
        from rodan.jobs.helloworld.helloworld import HelloWorld3

        app.register_task(HelloWorld3())
    except ImportError:
        pass

    # Register HPC Fast Trainer
    try:
        from rodan.jobs.hpc_fast_trainer.hpc_fast_trainer import HPCFastTrainer

        app.register_task(HPCFastTrainer())
    except ImportError:
        pass

    # Register PIL Rodan
    try:
        from rodan.jobs.pil_rodan.red_filtering import RedFilter

        app.register_task(RedFilter())
    except ImportError:
        pass

    try:
        from rodan.jobs.pil_rodan.resize import resize

        app.register_task(resize())
    except ImportError:
        pass

    try:
        from rodan.jobs.pil_rodan.to_jpeg2000 import to_jpeg2000

        app.register_task(to_jpeg2000())
    except ImportError:
        pass

    try:
        from rodan.jobs.pil_rodan.to_png import to_png

        app.register_task(to_png())
    except ImportError:
        pass

    try:
        from rodan.jobs.pil_rodan.to_tiff import to_tiff

        app.register_task(to_tiff())
    except ImportError:
        pass


# GPU Jobs
def register_gpu():

    # Register Calvo
    # try:
    #     from rodan.jobs.Calvo_classifier.calvo_classifier import CalvoClassifier

    #     app.register_task(CalvoClassifier())
    # except ImportError:
    #     print("Calvo Classifier failed to import.")

    # try:
    #     from rodan.jobs.Calvo_classifier.calvo_trainer import CalvoTrainer

    #     app.register_task(CalvoTrainer())
    # except ImportError:
    #     print("Calvo Trainer failed to import.")

    # try:
    #     from rodan.jobs.Calvo_classifier.fast_calvo_classifier import (
    #         FastCalvoClassifier,
    #     )

    #     app.register_task(FastCalvoClassifier())
    # except ImportError:
    #     print("Fast Calvo Classifier failed to import.")

    # try:
    #     from rodan.jobs.Calvo_classifier.fast_calvo_trainer import FastCalvoTrainer

    #     app.register_task(FastCalvoTrainer())
    # except ImportError:
    #     print("Fast Calvo Trainer failed to import.")

    # Register Text Alignment
    try:
        from rodan.jobs.text_alignment.text_alignment import text_alignment

        app.register_task(text_alignment())
    except ImportError:
        pass


if __name__ == "__main__":
    register_all()
