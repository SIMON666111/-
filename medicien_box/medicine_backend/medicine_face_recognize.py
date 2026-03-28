import time
import os
import threading
from datetime import datetime

import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-face_recognition-thirdex")
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-unihiker_wifi-thirdex")
from unihiker import GUI
from unihiker_connet_wifi import *
from pinpong.board import Board,Pin
from pinpong.extension.unihiker import *
u_gui=GUI()

import cv2
import numpy as np
import train_model  # custom train model module
from PIL import Image, ImageDraw, ImageFont # import PIL library (for drawing Chinese chars)

from pinpong.board import Board,Pin
from pinpong.extension.unihiker import *

############################################################################################################################################################
                                                        # face recognition related functions
def numberMap(x, in_min, in_max, out_min, out_max):
    """
    number mapping function
    map a number from one range to another
    params:
        x: input value
        in_min: input min
        in_max: input max
        out_min: output min
        out_max: output max
    returns:
        mapped value
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def drawChinese(text, x, y, size, r, g, b, a, img):
    """
    draw chinese character function
    params:
        text: text to draw
        x, y: draw position
        size: font size
        r, g, b, a: color value (RGBA)
        img: image to draw on
    returns:
        image after drawing
    """
    font = ImageFont.truetype("HYQiHei_50S.ttf", size)  # load chinese font
    img_pil = Image.fromarray(img)  # convert to PIL image
    draw = ImageDraw.Draw(img_pil)  # create draw object
    draw.text((x, y), text, font=font, fill=(b, g, r, a))  # draw text (note color order is BGR)
    frame = np.array(img_pil)  # convert back to numpy array
    return frame

def countdown_thread(event):
    for i in range(3600, 0, -1):
        print(f"background countdown: {i} seconds")
        time.sleep(1)
    print("countdown finished!")
    # set event
    event.set()

def start_countdown():
    # create event object
    event = threading.Event()
    # create and start background thread
    t = threading.Thread(target=countdown_thread, args=(event,), daemon=True)
    t.start()
    print("background countdown started!")
    return event
###################################################################################################################################################
                                                        # face recognition class
class face_recognition():
    def __init__(self):
        id_list=[]
    def append_face_data(self,face_id):
        face__id = face_id # category id
        cap = cv2.VideoCapture(0)  # open default camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # set width
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # set height
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # set buffer size
        # create fullscreen window
        cv2.namedWindow('cvwindow', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('cvwindow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # counter init
        pic_counta = 0  # photo counter
        font = cv2.FONT_HERSHEY_SIMPLEX  # font
        # wait for camera to open
        while not cap.isOpened():
            continue
        print('sucessfully open cap')
        # load face detector and recognizer
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # face detection classifier
        recognizer = cv2.face.LBPHFaceRecognizer_create()  # LBPH face recognizer
        # wait for user press 'a' to start
        while not (cv2.waitKey(10) == ord('a')):
            time.sleep(0.1)
        print('successfulyy press a')
        # collect 50 face photos
        while not (pic_counta >= 50):
            cvimg_success, img_src = cap.read()  # read camera frame
            if not cvimg_success:
                continue
                
            # image processing: crop and resize
            cvimg_h, cvimg_w, cvimg_c = img_src.shape
            cvimg_w1 = cvimg_h * 240 // 320  # calculate width (keep 240:320 ratio)
            cvimg_x1 = (cvimg_w - cvimg_w1) // 2  # calculate start X coordinate
            img_src = img_src[:, cvimg_x1:cvimg_x1 + cvimg_w1]  # crop image
            img_src = cv2.resize(img_src, (240, 320))  # resize
            
            # convert to grayscale (needed for face detection)
            gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)

            if pic_counta < 50:  # haven't taken 50 yet
                cv2.putText(img_src, 'shooting', (10, 30), font, 0.8, (0, 255, 0), 2)
            # detect faces
            faces = detector.detectMultiScale(gray, 1.3, 5)  # params: image, scale factor, min neighbors
            
            # show original image
            cv2.imshow('cvwindow', img_src)
            
            # set save path (category id)
            img_dir_path = "/root/face_recognition/picture/" + str(face__id) + "/"
            img_name_path = str(datetime.now().strftime('%Y%m%d_%H%M%S_%f')) + ".jpg"  # name with timestamp
            img_save_path = img_dir_path + img_name_path
            
            # check and create directory
            try:
                if not os.path.exists(img_dir_path):
                    print("The folder does not exist, created automatically")
                    os.system("mkdir -p /root/face_recognition/picture/" + str(face__id) + "/")  # create dir
            except IOError:
                print("IOError, created automatically")
                break
            
            # process detected faces
            for (x, y, w, h) in faces:
                # draw face rectangle
                cv2.rectangle(img_src, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # save photo
                if pic_counta <= 50:
                    cv2.putText(img_src, f'shooting amount{pic_counta}', (10, 50), font, 0.6, (0, 255, 0), 2)  # show "shooting"
                    cv2.imwrite(img_save_path, img_src)  # save image
                    pic_counta += 1  # counter +1
                    print("save picture path:", img_save_path)  # print save path
                    print("save 0-picture count:" + str(pic_counta))  # print save count
                    cv2.putText(img_src, '0', (x, y + h), font, 0.6, (0, 0, 255), 2)  # show category label
                    time.sleep(0.05)  # short pause
                else:
                    cv2.putText(img_src, 'Done, Please quit', (10, 50), font, 0.6, (0, 255, 0), 2)  # show "done"
                    time.sleep(2)
            
            # show processed image
            cv2.imshow('cvwindow', img_src)
            cv2.waitKey(5)  # wait 5ms
        

        # release camera resource
        cap.release()
        cv2.destroyAllWindows()
        u_gui.draw_text(text="photo shooting done, training model",x=0,y=0,font_size=10, color="#0000FF")

        # re-init detector and recognizer
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        # train model
        faces, Ids = train_model.get_images_and_labels('/root/face_recognition/picture/')  # get images and labels
        recognizer.train(faces, np.array(Ids))  # train model

        # save model
        img_dir_path = "/root/face_recognition/model/model.yml"
        img_dir_path = os.path.abspath(os.path.dirname(img_dir_path))  # get directory path
        print(img_dir_path)

        # check and create directory
        try:
            if not os.path.exists(img_dir_path):
                print("The folder does not exist, created automatically")
                os.mkdir(img_dir_path)  # create dir
        except IOError:
            print("IOError, created automatically")

        # save model file
        u_gui.clear()
        u_gui.draw_text(text="model training done",x=0,y=0,font_size=20, color="#0000FF")
        recognizer.save("/root/face_recognition/model/model.yml")
        print("model training completed and saved")
        time.sleep(2)
        u_gui.clear()
    def face_recognition(self,face_id):
        face__id=face_id
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
        event=start_countdown()
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
            if event.is_set():
                break
            if len(faces)>0:
                img_id, confidence = 0,0
                for (x, y, cvimg_w, cvimg_h) in faces:
                    cv2.rectangle(img_src, (x - 10, y - 10), (x + cvimg_w + 10, y + cvimg_h + 10), (0, 255, 0), 2)
                    img_array = gray[y:y + cvimg_h, x:x + cvimg_w]
                    img_id, confidence = recognizer.predict(img_array)
                    confidence   = (numberMap(confidence, 150, 0,0,100))
                    if confidence ==100:
                        confidence = 0
                if img_id==face__id and confidence > 60:
                    break
                print((str("index:") + str((str(img_id) + str((str("confidence:") + str(confidence)))))))
            cv2.imshow('cvwindow', img_src)
            cv2.waitKey(5)
        if not event.is_set():
            return True
        else:
            return False
