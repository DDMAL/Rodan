from rodan.celery import app
import yaml
from yaml.loader import SafeLoader

import os
import environ
import importlib
"""
Script for registering Rodan jobs with Celery, split into their respective queues
"""
ROOT_DIR = environ.Path(__file__) - 2
PROJECT_PATH = ROOT_DIR.path("rodan")

# Open the file and load the file
with open(os.path.join(os.path.dirname(PROJECT_PATH), 'registerJobs.yaml')) as file:
    allJobs = yaml.load(file, Loader=SafeLoader)

BASE_JOB_PACKAGES = [base_jobs for base_jobs in allJobs['BASE_JOB_PACKAGES']]
RODAN_PYTHON3_JOBS = [py3_jobs for py3_jobs in allJobs['RODAN_PYTHON3_JOBS']]
RODAN_GPU_JOBS = [gpu_jobs for gpu_jobs in allJobs['RODAN_GPU_JOBS']]

# Register all jobs
def register_all():
    # Register all jobs
    register_base()
    register_py3()
    register_gpu()


# base jobs
def register_base():

    for path in allJobs['BASE_JOB_PACKAGES']:
        for base_job in allJobs['BASE_JOB_PACKAGES'][path]:
            try: 
                # from path import base_job as job_name
                j = getattr(importlib.import_module(path), base_job)                
                app.register_task(j)

            except Exception as exception:
                print(base_job + " failed to import with the following error:",  exception.__class__.__name__)

# Python3 Jobs
def register_py3():
    for pack in allJobs['RODAN_PYTHON3_JOBS']:
        for path in allJobs['RODAN_PYTHON3_JOBS'][pack]:
            for py3_job in allJobs['RODAN_PYTHON3_JOBS'][pack][path]:
                try: 
                    #from path import py3_job as job_name
                    j = getattr(importlib.import_module(path), py3_job)  
                    app.register_task(j)

                except Exception as exception:
                    print(py3_job + " failed to import with the following error:",  exception.__class__.__name__)


    # Register Hello World
#     try:
#         from rodan.jobs.helloworld.helloworld import HelloWorld

#         app.register_task(HelloWorld())
#     except Exception as exception:
#         import_name = "Hello World"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.helloworld.helloworld import HelloWorldMultiPort

#         app.register_task(HelloWorldMultiPort())
#     except Exception as exception:
#         import_name = "Hello World Multi Port"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.helloworld.helloworld import HelloWorld3

#         app.register_task(HelloWorld3())
#     except Exception as exception:
#         import_name = "Hello World Python3"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     # Register MEI resizing
#     try:
#         from rodan.jobs.MEI_resizing.mei_resize import MEI_Resize

#         app.register_task(MEI_Resize())
#     except Exception as exception:
#         import_name = "MEI Resizing"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)



#     # Register PIL Rodan
#     try:
#         from rodan.jobs.pil_rodan.red_filtering import RedFilter

#         app.register_task(RedFilter())
#     except Exception as exception:
#         import_name = "PIL Red Filter"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.pil_rodan.resize import resize

#         app.register_task(resize())
#     except Exception as exception:
#         import_name = "PIL Resize"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)


#     try:
#         from rodan.jobs.pil_rodan.to_png import to_png

#         app.register_task(to_png())
#     except Exception as exception:
#         import_name = "PIL To PNG"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.pil_rodan.to_tiff import to_tiff

#         app.register_task(to_tiff())
#     except Exception as exception:
#         import_name = "PIL To TIFF"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)
    
#     try:
#         from rodan.jobs.mei2vol_wrapper.m2v_wrapper import MEI2Vol
#         app.register_task(MEI2Vol())
#     except Exception as exception:
#         import_name = "MEI2Volpiano"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)
    
#     # Register Gamera
#     try:
#         from rodan.jobs.gamera_rodan.wrappers.classification import ClassificationTask

#         app.register_task(ClassificationTask())
#     except Exception as exception:
#         import_name = "Classification"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.binarization import (
#             gamera_gatos_background,
#         )

#         app.register_task(gamera_gatos_background())
#     except Exception as exception:
#         import_name = "Gatos Background"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.binarization import (
#             gamera_gatos_threshold,
#         )

#         app.register_task(gamera_gatos_threshold())
#     except Exception as exception:
#         import_name = "Gatos Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.binarization import (
#             gamera_brink_threshold,
#         )

#         app.register_task(gamera_brink_threshold())
#     except Exception as exception:
#         import_name = "Brink Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.binarization import (
#             gamera_sauvola_threshold,
#         )

#         app.register_task(gamera_sauvola_threshold())
#     except Exception as exception:
#         import_name = "Sauvola Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.binarization import (
#             gamera_niblack_threshold,
#         )

#         app.register_task(gamera_niblack_threshold())
#     except Exception as exception:
#         import_name = "Niblack Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.cc_analysis import (
#             CCAnalysis,
#         )

#         app.register_task(CCAnalysis())
#     except Exception as exception:
#         import_name = "CC Analysis"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.image_conversion import (
#             gamera_to_rgb,
#         )

#         app.register_task(gamera_to_rgb())
#     except Exception as exception:
#         import_name = "To RGB"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.image_conversion import (
#             gamera_to_greyscale,
#         )

#         app.register_task(gamera_to_greyscale())
#     except Exception as exception:
#         import_name = "To Greyscale"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.image_conversion import (
#             gamera_to_grey16,
#         )

#         app.register_task(gamera_to_grey16())
#     except Exception as exception:
#         import_name = "To Grey16"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.image_conversion import (
#             gamera_to_onebit,
#         )

#         app.register_task(gamera_to_onebit())
#     except Exception as exception:
#         import_name = "To ONEBIT"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.image_utilities import (
#             gamera_invert,
#         )

#         app.register_task(gamera_invert())
#     except Exception as exception:
#         import_name = "Invert"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.morphology import (
#             gamera_despeckle,
#         )

#         app.register_task(gamera_despeckle())
#     except Exception as exception:
#         import_name = "Despeckle"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.morphology import (
#             gamera_dilate,
#         )

#         app.register_task(gamera_dilate())
#     except Exception as exception:
#         import_name = "Dilate"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.threshold import (
#             gamera_otsu_threshold,
#         )

#         app.register_task(gamera_otsu_threshold())
#     except Exception as exception:
#         import_name = "Otsu Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.threshold import (
#             gamera_tsai_moment_preserving_threshold,
#         )

#         app.register_task(gamera_tsai_moment_preserving_threshold())
#     except Exception as exception:
#         import_name = "Tsai Moment Preserving Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.threshold import (
#             gamera_abutaleb_threshold,
#         )

#         app.register_task(gamera_abutaleb_threshold())
#     except Exception as exception:
#         import_name = "Abutaleb Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.threshold import (
#             gamera_bernsen_threshold,
#         )

#         app.register_task(gamera_bernsen_threshold())
#     except Exception as exception:
#         import_name = "Bernsen Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.plugins.threshold import (
#             gamera_djvu_threshold,
#         )

#         app.register_task(gamera_djvu_threshold())
#     except Exception as exception:
#         import_name = "Djvu Threshold"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     # Register miyao toolkit jobs
#     try:
#         from rodan.jobs.gamera_rodan.wrappers.toolkits.music_staves.miyao import (
#             MiyaoStaffFinder,
#         )

#         app.register_task(MiyaoStaffFinder())
#     except Exception as exception:
#         import_name = "Miyao Staff Finder"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)


#    # Register Biollante
#     try:
#         from rodan.jobs.biollante_rodan import BiollanteRodan

#         app.register_task(BiollanteRodan())
#     except Exception as exception:
#         import_name = "Biollante"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)
    
    
#     # Register IC
#     try:
#         from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier

#         app.register_task(InteractiveClassifier())
#     except Exception as exception:
#         import_name = "Interactive Classifier"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.interactive_classifier.gamera_xml_distributor import (
#             GameraXMLDistributor,
#         )

#         app.register_task(GameraXMLDistributor())
#     except Exception as exception:
#         import_name = "XML Distributor"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalAnd

#         app.register_task(GameraMaskLogicalAnd())
#     except Exception as exception:
#         import_name = "Logical And"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.gamera_rodan.wrappers.masking import GameraMaskLogicalXor

#         app.register_task(GameraMaskLogicalXor())
#     except Exception as exception:
#         import_name = "Logical Xor"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)
#     # Register Neume Slicing
#     try:
#         from rodan.jobs.diagonal_neume_slicing.base import DiagonalNeumeSlicing

#         app.register_task(DiagonalNeumeSlicing())
#     except Exception as exception:
#         import_name = "Diagonal Neume Slicing"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.diagonal_neume_slicing.base import DirtyLayerRepair

#         app.register_task(DirtyLayerRepair())
#     except Exception as exception:
#         import_name = "Dirty Layer Repair"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    
#     # Register HPF
#     try:
#         from rodan.jobs.heuristic_pitch_finding.base import MiyaoStaffinding

#         app.register_task(MiyaoStaffinding())
#     except Exception as exception:
#         import_name = "Miyao Staff Finding"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     try:
#         from rodan.jobs.heuristic_pitch_finding.base import HeuristicPitchFinding

#         app.register_task(HeuristicPitchFinding())
#     except Exception as exception:
#         import_name = "Heuristic Pitch Finding"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)


#     # Register MEI Encoding
#     try:
#         from rodan.jobs.MEI_encoding.MEI_encoding import MEI_encoding

#         app.register_task(MEI_encoding())
#     except Exception as exception:
#         import_name = "MEI Encoding"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     # Register HPC Fast Trainer
#     try:
#         from rodan.jobs.hpc_fast_trainer.hpc_fast_trainer import HPCFastTrainer

#         app.register_task(HPCFastTrainer())
#     except Exception as exception:
#         import_name = "HPC Fast Trainer"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#      # Register Neon
#     try:
#         from rodan.jobs.neon_wrapper.wrapper import Neon

#         app.register_task(Neon())
#     except Exception as exception:
#         import_name = "Neon"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

#     # Register Pixel.js
#     try:
#         from rodan.jobs.pixel_wrapper.wrapper import PixelInteractive

#         app.register_task(PixelInteractive())
#     except Exception as exception:
#         import_name = "Pixel"
#         print(import_name + " failed to import with the following error:", exception.__class__.__name__)

# GPU Jobs
def register_gpu():

    # Register Calvo
    try:
        from rodan.jobs.Calvo_classifier.calvo_classifier import CalvoClassifier

        app.register_task(CalvoClassifier())
    except Exception as exception:
        import_name = "Calvo Classifier"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    try:
        from rodan.jobs.Calvo_classifier.calvo_trainer import CalvoTrainer

        app.register_task(CalvoTrainer())
    except Exception as exception:
        import_name = "Calvo Trainer"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    try:
        from rodan.jobs.Calvo_classifier.fast_calvo_classifier import (
            FastCalvoClassifier,
        )

        app.register_task(FastCalvoClassifier())
    except Exception as exception:
        import_name = "Fast Calvo Classifier"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    try:
        from rodan.jobs.Calvo_classifier.fast_calvo_trainer import FastCalvoTrainer

        app.register_task(FastCalvoTrainer())
    except Exception as exception:
        import_name = "Fast Calvo Trainer"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    # Register Text Alignment
    try:
        from rodan.jobs.text_alignment.text_alignment import text_alignment

        app.register_task(text_alignment())
    except Exception as exception:
        import_name = "Text Alignment"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    # Register Paco's Trainer
    try:
        from rodan.jobs.Paco_classifier.fast_paco_trainer import FastPacoTrainer

        app.register_task(FastPacoTrainer())
    except Exception as exception:
        import_name = "Paco Trainer"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    # Register Paco's Classifier
    try:
        from rodan.jobs.Paco_classifier.fast_paco_classifier import FastPacoClassifier

        app.register_task(FastPacoClassifier())
    except Exception as exception:
        import_name = "Paco Classifier"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    # Register background_removal
    try:
        from rodan.jobs.background_removal.BgRemovalRodan import BgRemoval
        app.register_task(BgRemoval())
    except Exception as exception:
        import_name = "Background Removal"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)

    # Register SAE binarization
    try:
        from rodan.jobs.SAE_binarization.SAE_binarization import SAE_binarization
        app.register_task(SAE_binarization())
    except Exception as exception:
        import_name = "SAE binarization"
        print(import_name + " failed to import with the following error:", exception.__class__.__name__)


if __name__ == "__main__":
    register_all()
