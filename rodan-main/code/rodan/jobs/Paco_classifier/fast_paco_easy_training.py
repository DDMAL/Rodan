"""Local Fast Trainer
This is the file for running Calvo Fast Trainer loaclly. Make sure
to have an 'Images' folder with the correct inputs in the same directory.
If not, you can change the values in 'inputs' and 'outputs'.

Simply run `python local_fast_trainer.py` to see the output.
This will call `training_engine_sae.py`.

It should generate 3 files in its current state. A background model,
a Model 0, and a Log File.

If you're running it in a Rodan container, this will be located in code/Rodan/rodan/jobs/Calvo_classifier
If the container is already running, try `docker exec -it [container_name] bash` to run the script without
stopping.
"""

import logging
import os
import sys

print (sys.path)
import cv2
import numpy as np
import training_engine_sae as training
import pdb
import argparse
from input_settings_test import pre_training_check


# ===========================
#       CONSTANTS
# ===========================
KEY_BACKGROUND_LAYER = "rgba PNG - Layer 0 (Background)"
KEY_SELECTED_REGIONS = "rgba PNG - Selected regions"
KEY_RESOURCE_PATH = "resource_path"

kPATH_IMAGES_DEFAULT = "datasets/images"
kPATH_REGION_MASKS_DEFAULT = "datasets/regions"
kPATH_BACKGROUND_DEFAULT = "datasets/layers/background"
kPATH_LAYERS_DEFAULT = ["datasets/layers/staff", "datasets/layers/neumes"]
kPATH_OUTPUT_MODELS_DEFAULT = ["Models/model_background.h5", "Models/model_staff.h5", "Models/model_neumes.h5"]
kBATCH_SIZE_DEFAULT = 8
kPATCH_HEIGHT_DEFAULT = 256
kPATCH_WIDTH_DEFAULT = 256
kMAX_NUMBER_OF_EPOCHS_DEFAULT = 1
kNUMBER_SAMPLES_PER_CLASS_DEFAULT = 100
kEARLY_STOPPING_PATIENCE_DEFAULT = 15
kFILE_SELECTION_MODE_DEFAULT = training.FileSelectionMode.SHUFFLE
kSAMPLE_EXTRACTION_MODE_DEFAULT = training.SampleExtractionMode.RANDOM
# ===========================


def menu():
    parser = argparse.ArgumentParser(description='Fast trainer')

    parser.add_argument(
                    '-psr',  
                    default=kPATH_IMAGES_DEFAULT, 
                    dest='path_src', 
                    help='Path of the source folder that contains the original images.'
                    )

    parser.add_argument(
                    '-prg',  
                    default=kPATH_REGION_MASKS_DEFAULT,
                    dest='path_regions', 
                    help='Path of the folder that contains the region masks.'
                    )

    parser.add_argument(
                    '-pbg',  
                    default=kPATH_BACKGROUND_DEFAULT,
                    dest='path_bg', 
                    help='Path of the folder with the background layer data.'
                    )

    parser.add_argument(
                    '-pgt',
                    dest='path_layer', 
                    help='Paths of the ground-truth folders to be considered (one per layer).', 
                    action='append'
                    )
    
    parser.add_argument(
                    '-out',
                    dest='path_out', 
                    help='Paths for the models saved after the training.', 
                    action='append'
                    )

    parser.add_argument(
                    '-width',
                    default=kPATCH_HEIGHT_DEFAULT,
                    dest='patch_width',
                    type=int,
                    help='Patch width'
                    )

    parser.add_argument(
                    '-height',
                    default=kPATCH_WIDTH_DEFAULT,
                    dest='patch_height',
                    type=int,
                    help='Patch height'
                    )

    parser.add_argument(
                    '-b',
                    default=kBATCH_SIZE_DEFAULT,
                    dest='batch_size',
                    type=int,
                    help='Batch size'
                    )

    parser.add_argument(
                    '-e',
                    default=kMAX_NUMBER_OF_EPOCHS_DEFAULT,
                    dest='max_epochs',
                    type=int,
                    help='Maximum number of epochs'
                    )

    parser.add_argument(
                    '-n',
                    default=kNUMBER_SAMPLES_PER_CLASS_DEFAULT,
                    dest='number_samples_per_class',
                    type=int,
                    help='Number of samples per class to be extracted'
                    )

    parser.add_argument(
                    '-fm',
                    default=kFILE_SELECTION_MODE_DEFAULT, 
                    dest='file_selection_mode',
                    type=training.FileSelectionMode.from_string, 
                    choices=list(training.FileSelectionMode), 
                    help='Mode of selecting images in the training process'
                    )

    parser.add_argument(
                    '-sm',
                    default=kSAMPLE_EXTRACTION_MODE_DEFAULT, 
                    dest='sample_extraction_mode',
                    type=training.SampleExtractionMode.from_string, 
                    choices=list(training.SampleExtractionMode), 
                    help='Mode of extracing samples for each image in the training process'
                    )

    parser.add_argument(
                    '-pat',
                    default=kEARLY_STOPPING_PATIENCE_DEFAULT,
                    dest='patience',
                    type=int,
                    help='Number of epochs of patience for the early stopping. If the model does not improves the training results in this number of consecutive epochs, the training is stopped.'
                    )

    args = parser.parse_args()

    args.path_layer = args.path_layer if args.path_layer is not None else kPATH_LAYERS_DEFAULT
    args.path_out = args.path_out if args.path_out is not None else kPATH_OUTPUT_MODELS_DEFAULT
    

    print('CONFIG:\n -', str(args).replace('Namespace(','').replace(')','').replace(', ', '\n - '))

    return args

# Return the list of files in folder
# ext param is optional. For example: 'jpg' or 'jpg|jpeg|bmp|png'
def list_files(directory, ext=None):
    list_files =  [os.path.join(directory, f) for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and ( ext==None or re.match('([\w_-]+\.(?:' + ext + '))', f) )]

    return sorted(list_files)

#Initialize the dictionary with the inputs
def init_input_dictionary(config):
    inputs = {}

    inputs["Image"] = []
    inputs[KEY_BACKGROUND_LAYER] = []
    inputs[KEY_SELECTED_REGIONS] = []

    idx_layer = 1
    for path_layer in config.path_layer:
            name_layer = "rgba PNG - Layer " + str(idx_layer)
            idx_layer+=1

            inputs[name_layer] = []

    list_src_files = list_files(config.path_src)

    for path_img in list_src_files:

        print (path_img)
        dict_img = {}
        dict_img[KEY_RESOURCE_PATH] = path_img
        inputs["Image"].append(dict_img)

        filename_img = os.path.basename(path_img)

        #list_bg_files = list_files(config.path_bg) #background

        path_bg = os.path.join(config.path_bg, filename_img)

        dict_img = {}
        dict_img[KEY_RESOURCE_PATH] = path_bg
        inputs[KEY_BACKGROUND_LAYER].append(dict_img)


        filename_without_ext, ext = os.path.splitext(filename_img)
        filename_png = filename_without_ext + ".png"

        path_regions = os.path.join(config.path_regions, filename_png)
        dict_img = {}
        dict_img[KEY_RESOURCE_PATH] = path_regions
        inputs[KEY_SELECTED_REGIONS].append(dict_img)
        

        idx_layer = 1
        for path_layer in config.path_layer:
            fullpath_layer = os.path.join(path_layer, filename_img)
            name_layer = "rgba PNG - Layer " + str(idx_layer)
            idx_layer+=1

            dict_img = {}
            dict_img[KEY_RESOURCE_PATH] = fullpath_layer
            inputs[name_layer].append(dict_img)
            
    return inputs

#Initialize the dictionary with the outputs
def init_output_dictionary(config):
    outputs = {}

    idx_model = 0
    for path_model in config.path_out:
        name_model = "Model " + str(idx_model)
        idx_model+=1
        outputs[name_model] = []

    idx_model = 0
    for path_model in config.path_out:
        name_model = "Model " + str(idx_model)
        idx_model += 1
        
        dict_img = {}
        dict_img[KEY_RESOURCE_PATH] = path_model
        outputs[name_model].append(dict_img)

    return outputs


#########################################################################

config = menu()

# Fail if arbitrary layers are not equal before training occurs.

inputs = init_input_dictionary(config)
outputs = init_output_dictionary(config)

# Sanity check
pre_training_check(inputs, config.batch_size, config.patch_height, config.patch_width, config.number_samples_per_class)

input_ports = len([x for x in inputs if "Layer" in x])
output_ports = len([x for x in outputs if "Model" in x or "Log file" in x])
if input_ports not in [output_ports, output_ports - 1]: # So it still works if Log File is added as an output. 
    raise Exception(
        'The number of input layers "rgba PNG - Layers" does not match the number of'
        ' output "Adjustable models"\n'
        "input_ports: " + str(input_ports) + " output_ports: " + str(output_ports)
    )

# Create output models
output_models_path = {}

for i in range(input_ports):
    output_models_path[str(i)] = outputs["Model " + str(i)][0][KEY_RESOURCE_PATH]
    # THIS IS NOT TAKING INTO ACCOUNT ANY FILE NOT NAMED MODEL IE BACKGROUND AND LOG!!!!

# Call in training function
status = training.train_msae(
    inputs=inputs,
    num_labels=input_ports,
    height=config.patch_height,
    width=config.patch_width,
    output_path=output_models_path,
    file_selection_mode=config.file_selection_mode,
    sample_extraction_mode=config.sample_extraction_mode,
    epochs=config.max_epochs,
    number_samples_per_class=config.number_samples_per_class,
    batch_size=config.batch_size,
    patience=config.patience
)

# THIS IS ONLY CREATING THE MODEL 0 FILE!!!!!!
print("Finishing the Fast CM trainer job.")


