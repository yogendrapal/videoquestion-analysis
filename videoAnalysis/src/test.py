'''

Github link of original code: https://github.com/oarriaga/face_classification/blob/master/report.pdf

Author: Neel Dani
Date: 22nd May, 2019

Incroporated few changes according to needs mentioned below.

CHANGES INCORPORATED:

1) Used skvideo.io package to read a video rather than openCV as video maybe rotated (landscape mode). 
Skvideo.io also reads metdata about the video, a provision missing in OpenCV.

2) Used cvlib (SSD model of OpenCV) for face detection which performs better than the Haar Cascade. 
Haar Cascade detects only frontal faces.

3) Read video as a JSON object and write the ouput (tags of gender, emotion etc) as a JSON file
so that it is easily accessible from cloud.

4) P(female) > 0.4 and not 0.5. This change is incorporated as the CNN gender model is trained on faces 
of Western people. As a result, it has a bias towards Westerneres and doesnt work perfectly on Indian images.
The model thus makes mistakes by predicting female as male. Hence to remove this bias, P(female) > 0.4 instead of 0.5.
  
5)Evaluation metric is calculated by taking majority of the last "n" (frame_wndow) frames.   

'''


'''

TO DO

1) Face alignment algorithm after face detection for better prediction.

2) Merge age prediction code with gender and expression prediction.


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

#added imports to support changes
import skvideo.io
from utils.inference import apply_offset
import cvlib as cv
import json

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

# Count of the genders predicted for each frame. Final prediction will be max(male_count, female_count)
gender_count = {"man": 0, "woman": 0}

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
gender_model_path = '../trained_models/gender_models/simple_CNN.81-0.96.hdf5'

#path to video
path = "/home/neel/IITB/face_classification/images/dimpal.mp4"

#JSON file paths
json_files_path = "../json_files/"
json_video_load_path = json_files_path + "video_path.json"

with open(json_video_load_path, 'r') as infile:
    video_path = json.loads(infile.read())
video_name = video_path["path"].split('/')[-1].split('.')[0]
json_tag_write_path = json_files_path + video_name + ".json"

print(json_video_load_path)
print(video_path)
print(video_name)
print(json_tag_write_path)

emotion_labels = get_labels('fer2013')
gender_labels = get_labels('imdb')
font = cv2.FONT_HERSHEY_SIMPLEX

# hyper-parameters for bounding boxes shape
frame_window = 10

# Buffer for bounding boxes for gender
gender_offsets = (30, 60) 

# Buffer for bounding boxes for emotion
emotion_offsets = (20, 40) 

#No. of faces required
num_faces = 1

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
gender_classifier = load_model(gender_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3] #requires input shape of (64, 64) for fer2013_mini_XCEPTION.102-0.66.hdf5
gender_target_size = gender_classifier.input_shape[1:3] #requires input shape of (48, 48) simple_CNN.81-0.96.hdf5'

print("Emotion target size: ", emotion_target_size)
print("Gender target size: ", gender_target_size)

# starting lists for calculating modes
gender_window = []
emotion_window = []

# starting video streaming
cv2.namedWindow('window_frame')
videogen = skvideo.io.vreader(video_path["path"])

for bgr_image in videogen:

    bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_RGB2BGR)
    frame_dim = bgr_image.shape[:2]
    
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    #Detect multiple face coooridnates along with their confidences using SSD from cvlib library
    faces, confidences = cv.detect_face(bgr_image)

    for detected_faces_index in range(min(len(faces), num_faces)):
        
        '''
        extract co-ordinates of the detected face.
        (startX, startY) is the bottom-left co-orinate of the detected face.
        (endX, endY) is the top-right co-ordinate of the detected face.
        '''
        face_coordinates = faces[detected_faces_index]
        startX, startY, endX, endY = face_coordinates

        #Transform co-ordinates from (x1, y1, x2, y2) to (x1, y1, width, height)
        face_coordinates = [startX, startY, endX-startX, endY-startY]
        x1, x2, y1, y2 = apply_offset(face_coordinates, gender_offsets, frame_dim) #for expanding the bounding box
        rgb_face = rgb_image[y1:y2, x1:x2]
        gray_face = gray_image[y1:y2, x1:x2]

        try:
            rgb_face = cv2.resize(rgb_face, (gender_target_size))
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        
        except:
            continue


        gray_face = preprocess_input(gray_face, False) #if true, it does normalization
        
        '''
        the below 2 lines involving np.expand_dims makes the 
        dim of the array from (x, y) to (1, x, y, 1). The first dim denotes the
        batch size and the last one denotes the no. of channels; grayscale in this case
        and hence 1. (3 in case of RBG).
        '''

        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)


        emotion_prob = emotion_classifier.predict(gray_face)
        emotion_label_arg = np.argmax(emotion_prob)
        emotion_label_prob = np.max(emotion_prob)
        emotion_text = emotion_labels[emotion_label_arg]
        emotion_window.append(emotion_text)

        rgb_face = np.expand_dims(rgb_face, 0)
        rgb_face = preprocess_input(rgb_face, False)
        gender_prediction = gender_classifier.predict(rgb_face)[0]
        gender_label_arg = np.argmax(gender_prediction)
        gender_label_prob = np.max(gender_prediction)
        gender_text = gender_labels[gender_label_arg]
        gender_window.append(gender_text)

        if len(gender_window) > frame_window:
            emotion_window.pop(0)
            gender_window.pop(0)

        try:
            emotion_mode = mode(emotion_window)
            gender_mode = mode(gender_window)

        except:
            continue

        if gender_text == gender_labels[0]:
            color = (0, 0, 255)
            gender_text += " " + str(gender_prediction[0])

        else:
            color = (255, 0, 0)
            gender_text += " " + str(gender_prediction[1])
        
        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, gender_text + str(gender_prediction[0]),
                  color, 0, -20, 1, 1)
        draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)

        #increment man or woman count based on the tag
        gender_count[gender_mode] += 1

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', bgr_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Man count: ", gender_count["man"])
print("Woman count: ", gender_count["woman"])
predicted_gender = max(gender_count, key=gender_count.get)
print("Predicted gender: ",  predicted_gender)

tags = {"Gender": predicted_gender}

with open(json_tag_write_path, 'w') as outfile:
    json.dump(tags, outfile)