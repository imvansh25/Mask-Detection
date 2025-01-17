# -*- coding: utf-8 -*-
"""FaceMaskforImage.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oxWMr3vVD9WG2BIcsFDM3L3VsVBGitXd
"""


from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import cv2
import os
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN
from imutils.video import VideoStream
import time
import imutils

def extract_face(image,required_size=(224, 224)):
  model = load_model("mask_detector.model")
  # convert to array
  pixels = asarray(image)
  # create the detector, using default weights
  detector = MTCNN()
  # detect faces in the image
  results = detector.detect_faces(pixels)
  # extract the bounding box from the first face
  face_array=[]
  for result in results:
    if result['confidence']<0.9:
      continue
    x1, y1, width, height = result['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    face = Image.fromarray(face)
    face = face.resize(required_size)
    face = asarray(face)
    face = preprocess_input(face)
    face = np.expand_dims(face, axis=0)
    (mask, withoutMask) = model.predict(face)[0]

    # determine the class label and color we'll use to draw
    # the bounding box and text
    label = "Mask" if mask > withoutMask else "No Mask"
    
    if label=="Mask":
      face_array.append((result,"green"))
    else:
      face_array.append((result,"red"))
    
 
  return face_array

from matplotlib.patches import Rectangle
def highlight_faces(image_path, faces):
  # display image
    image = plt.imread(image_path)
    plt.imshow(image)

    ax = plt.gca()

    # for each face, draw a rectangle based on coordinates
    for face,c in faces:
        x, y, width, height = face['box']
        face_border = Rectangle((x, y), width, height,linewidth=3,fill=False, color=c)
        ax.add_patch(face_border)
    plt.show()

def detect_face_mask_in_image(filename):
  img = cv2.imread(filename)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  highlight_faces(filename, extract_face(img))

#detect_face_mask_in_image("pic1.jpg")


def detect_face_in_video():
  vs = VideoStream(src=0).start()
  time.sleep(2.0)
  while True:
    frame = vs.read()
    if frame is None:
      continue
    frame = imutils.resize(frame, width=400)
    faces = extract_face(frame)
    for face,c in faces:
          x1, y1, width, height = face['box']
          x1, y1 = abs(x1), abs(y1)
          x2, y2 = x1 + width, y1 + height
          if c == 'green':
            c=(0,255,0)
          else:
            c=(0,0,255)
          cv2.rectangle(frame,(x2, y2),(x1, y1),c,2)
    cv2.imshow("Frame", frame)

    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF

	  # if the `q` key was pressed, break from the loop
    if key == ord("q"):
      break

  # do a bit of cleanup
  cv2.destroyAllWindows()
  vs.stop()

detect_face_in_video()