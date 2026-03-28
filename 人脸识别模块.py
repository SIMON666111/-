#  -*- coding: UTF-8 -*-

# MindPlus
# Python
import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-face_recognition-thirdex")
import time
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image


def numberMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def drawChinese(text,x,y,size,r, g, b, a,img):
    font = ImageFont.truetype("HYQiHei_50S.ttf", size)
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text((x,y), text, font=font, fill=(b, g, r, a))
    frame = np.array(img_pil)
    return frame

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cv2.namedWindow('cvwindow',cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('cvwindow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
pic_counta = 0
pic_countb = 0
font = cv2.FONT_HERSHEY_SIMPLEX
while not cap.isOpened():
    continue
detector=cv2.CascadeClassifier(cv2.data.haarcascades+ 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("/root/face_recognition/model/model.yml")
global img_id, confidence
img_id, confidence = 0,0
while True:

    cvimg_success, img_src = cap.read()
    cvimg_h, cvimg_w, cvimg_c = img_src.shape
    cvimg_w1 = cvimg_h*240//320
    cvimg_x1 = (cvimg_w-cvimg_w1)//2
    img_src = img_src[:, cvimg_x1:cvimg_x1+cvimg_w1]
    img_src = cv2.resize(img_src, (240, 320))
    gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)
    cv2.imshow('cvwindow', img_src)

    if len(faces)>0:
        img_id, confidence = 0,0
        for (x, y, cvimg_w, cvimg_h) in faces:
            cv2.rectangle(img_src, (x - 10, y - 10), (x + cvimg_w + 10, y + cvimg_h + 10), (0, 255, 0), 2)
            img_array = gray[y:y + cvimg_h, x:x + cvimg_w]
            img_id, confidence = recognizer.predict(img_array)
            confidence   = (numberMap(confidence, 150, 0,0,100))
            if confidence ==100:
                confidence = 0

        print(confidence)
    cv2.imshow('cvwindow', img_src)
    cv2.waitKey(5)
