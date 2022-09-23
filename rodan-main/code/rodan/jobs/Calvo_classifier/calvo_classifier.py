#-----------------------------------------------------------------------------
# Program Name:         calvo_classifier.py
# Program Description:  Rodan wrapper for Calvo's classifier
#-----------------------------------------------------------------------------

import cv2
import numpy as np
import os

from rodan.jobs.base import RodanTask


"""Wrap Calvo classifier in Rodan."""
    
class CalvoClassifier(RodanTask):
    name = "Pixelwise Analysis of Music Document"
    author = "Jorge Calvo-Zaragoza, Gabriel Vigliensoni, and Ichiro Fujinaga"
    description = "Given a pre-trained Convolutional neural network, the job performs a pixelwise analysis of music document images." 
    enabled = True
    category = "OMR - Layout analysis"
    interactive = False
    
    settings = {
        'title': 'Feature window',
        'job_queue': 'GPU',
        'type': 'object',
        'properties': {
            'Vertical span': {
                'type': 'integer',
                'minimum': 1,
                'default': 25
            },
            'Horizontal span': {
                'type': 'integer',
                'minimum': 1,
                'default': 25
            }
        }
    }
    
    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 1, 'resource_types': lambda mime: mime.startswith('image/')},
        {'name': 'Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5'] },
    )
    output_port_types = (
        {'name': 'Background', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Music symbol', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Staff lines', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Text', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']}
    )

    """
    Entry point
    """
    def run_my_task(self, inputs, settings, outputs):
        from . import recognition_engine as recognition
        # Ports
        image_filepath = inputs['Image'][0]['resource_path']
        model_filepath = inputs['Model'][0]['resource_path']        
        
        # Settings        
        vspan =  settings['Vertical span']
        hspan =  settings['Horizontal span']                
        
        # Process
        image = cv2.imread(image_filepath,True)            
        
        analysis = recognition.process_image(image,model_filepath,vspan,hspan)        
        
        # Let user define the number of labels?
        for label in range(0,4):
            lower_range = np.array(label, dtype=np.uint8)
            upper_range = np.array(label, dtype=np.uint8)
            mask = cv2.inRange(analysis, lower_range, upper_range)
            
            original_masked = cv2.bitwise_and(image,image,mask = mask)      
            original_masked[mask == 0] = (255, 255, 255)
        
            # Alpha = 0 when background
            alpha_channel = np.ones(mask.shape, dtype=mask.dtype)*255
            alpha_channel[mask == 0] = 0            
            b_channel, g_channel, r_channel = cv2.split(original_masked)
            original_masked_alpha = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
            
            if label == 0:
                port = 'Background'
            elif label == 1:
                port = 'Music symbol'
            elif label == 2:
                port = 'Staff lines'
            elif label == 3:
                port = 'Text'                
                
            if port in outputs:
                cv2.imwrite(outputs[port][0]['resource_path']+'.png',original_masked_alpha)   
                os.rename(outputs[port][0]['resource_path']+'.png',outputs[port][0]['resource_path'])
    

        return True
