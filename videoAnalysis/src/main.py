'''

Github link of original code: https://github.com/oarriaga/face_classification

Author: 

 Dani
Date: 22nd May, 2019

Incroporated few changes according to needs mentioned below.

CHANGES INCORPORATED:

1) Used skvideo.io package to read a video rather than openCV as video maybe rotated (landscape mode). 
Skvideo.io also reads metdata about the video, a provision missing in OpenCV.

2) Used cvlib (SSD model of OpenCV) for face detection which performs better than the Haar Cascade. 
Haar Cascade detects only frontal faces.

3) Read video as a JSON object and write the ouput (tags of gender, emotion etc) as a JSON file
so that it is easily accessible from cloud.

4)Evaluation metric is calculated by taking majority of the last "n" (frame_wndow) frames.   

5) Stored tags in JSON file format.



DONE BUT NOT INCORPORATED

1) Face alignment algorithm after face detection for better prediction.
(Made the code computationally heavy without any much difference in results)



TODO

1) Merge age prediction code with gender and expression prediction.


JSON should have following fields:
1) Filename
2) Timestamp pertaining to co-ordiantes of face
3) Face-co-ordinates, Confidence fora particular time-stamp(? Ask sir)
4) Gender tag

'''

from statistics import mode

import cv2
from keras.models import load_model
import numpy as np
import os

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input


#added imports to support changes
import skvideo.io
from utils.inference import apply_offset
import cvlib as cv
import json
import configparser

from utils.helper import get_json_tag_write_file
from utils.helper import get_predictions
from utils.helper import store_in_json_file
from utils.helper import get_video_path


#All parameters are stored in this file. Tweak parameters in config.ini for changes.
os.chdir("/home/aishwarya/videoquestion-analysis/videoAnalysis/src");
PATH_TO_CONFIG_FILE = "config.ini"

parser = configparser.ConfigParser()
parser.read(PATH_TO_CONFIG_FILE)

#Set path from config.ini
PATH = parser['PATH']
emotion_model_path      = PATH['emotion_model_path']
gender_model_path       = PATH['gender_model_path']
json_directory_path     = PATH['json_directory_path']
json_file_read_path     = PATH['json_file_read_path']

# Set queue size
QUEUE_SIZE              = parser['QUEUE_SIZE']
frame_window            = int(QUEUE_SIZE['frame_window'])

# Set bounding box cushion
BOUNDING_BOX_CUSHION    = parser['BOUNDING_BOX_CUSHION']
gender_offsets          = eval(BOUNDING_BOX_CUSHION['gender_offsets'])
emotion_offsets         = eval(BOUNDING_BOX_CUSHION['emotion_offsets'])

# Set no. of faces to detect
NO_OF_FACES_TO_DETECT   = parser['NO_OF_FACES_TO_DETECT']
num_faces               = int(NO_OF_FACES_TO_DETECT['num_faces'])

# Count of the genders predicted for each frame. Final prediction will be max(male_count, female_count)
gender_count            = {'man': 0, 'woman': 0}
emotions_count        = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}

video_path_in_json_file = json_directory_path + json_file_read_path
video_path              = get_video_path(video_path_in_json_file)
json_tag_write_path     = get_json_tag_write_file(video_path, json_directory_path)

#initialise the labels
emotion_labels          = get_labels('fer2013')
gender_labels           = get_labels('imdb')
font                    = cv2.FONT_HERSHEY_SIMPLEX

#load models
emotion_classifier      = load_model(emotion_model_path, compile=False)
gender_classifier       = load_model(gender_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size     = emotion_classifier.input_shape[1:3] #requires input shape of (64, 64) for fer2013_mini_XCEPTION.102-0.66.hdf5
gender_target_size      = gender_classifier.input_shape[1:3] #requires input shape of (48, 48) simple_CNN.81-0.96.hdf5'

# starting lists for calculating modes
gender_window = []
emotion_window = []
tags = {}


# starting video streaming
cv2.namedWindow('window_frame')
videogen = skvideo.io.vreader(video_path["path"])

for rgb_image in videogen:

    bgr_image          = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    frame_dim          = bgr_image.shape[:2]
    gray_image         = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)


    #Detect multiple face coooridnates along with their confidences using SSD from cvlib library
    faces, confidences = cv.detect_face(bgr_image)

    for detected_faces_index in range(min(len(faces), num_faces)):  
        
        '''
        extract co-ordinates of the detected face.
        (startX, startY) is the bottom-left co-orinate of the detected face.
        (endX, endY) is the top-right co-ordinate of the detected face.
        '''

        face_coordinates           = faces[detected_faces_index]
        startX, startY, endX, endY = face_coordinates


        # Transform co-ordinates from (x1, y1, x2, y2) to (x1, y1, width, height)
        face_coordinates    = [startX, startY, endX-startX, endY-startY]



        # Expanding the bounding box by add buffer (frame_size) 
        x1, x2, y1, y2      = apply_offset(face_coordinates, gender_offsets, frame_dim)
        rgb_face            = rgb_image[y1:y2, x1:x2]
        gray_face           = gray_image[y1:y2, x1:x2]




        try:
            rgb_face    = cv2.resize(rgb_face, (gender_target_size))
            bgr_face    = cv2.cvtColor(rgb_face, cv2.COLOR_RGB2BGR)
            gray_face   = cv2.resize(gray_face, (emotion_target_size))
        
        except:
            continue


        gray_face = preprocess_input(gray_face, False) #if 2nd parameter is true, pre_process_input also does normalization
        
        '''
        the below 2 lines involving np.expand_dims makes the 
        dim of the array from (x, y) to (1, x, y, 1). The first dim denotes the
        batch size and the last one denotes the no. of channels; grayscale in this case
        and hence 1. (3 in case of RBG).
        '''

        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)


        emotion_prob        = emotion_classifier.predict(gray_face)
        emotion_label_arg   = np.argmax(emotion_prob)
        emotion_label_prob  = np.max(emotion_prob)
        emotion_text        = emotion_labels[emotion_label_arg]
        emotion_window.append(emotion_text)

        rgb_face            = np.expand_dims(rgb_face, 0)
        rgb_face            = preprocess_input(rgb_face, False)
        gender_prediction   = gender_classifier.predict(rgb_face)[0]
        gender_label_arg    = np.argmax(gender_prediction)
        gender_label_prob   = np.max(gender_prediction)
        gender_text         = gender_labels[gender_label_arg]
        gender_window.append(gender_text)

        if len(gender_window) > frame_window:
            emotion_window.pop(0)
            gender_window.pop(0)

        try:
            emotion_mode    = mode(emotion_window)
            gender_mode     = mode(gender_window)

        except:
            continue

        if gender_text == gender_labels[0]:

            color           =   (0, 0, 255)
            gender_text     +=  " " + str(gender_prediction[0])

        else:
            color           =   (255, 0, 0)
            gender_text     +=  " " + str(gender_prediction[1])
        
        draw_bounding_box(face_coordinates, bgr_image, color)
        draw_text(face_coordinates, bgr_image, gender_text + str(gender_prediction[0]), color, 0, -20, 1, 1)
        draw_text(face_coordinates, bgr_image, emotion_mode, color, 0, -45, 1, 1)

        #increment man or woman count based on the tag
        gender_count[gender_mode]           += 1
        emotions_count[emotion_mode]   += 1
    
    cv2.imshow('window_frame', bgr_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


predicted_gender = get_predictions(gender_count)
predicted_emotions = get_predictions(emotions_count, 3)
tags['Gender'] = predicted_gender
tags['Emotions'] = predicted_emotions
print(tags)
store_in_json_file(tags, json_tag_write_path)
