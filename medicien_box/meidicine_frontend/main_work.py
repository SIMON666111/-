from pywebio.input import input,select,actions,slider
from pywebio.output import put_text,put_button,use_scope,clear,put_table,put_html,popup
from pywebio import start_server
from pywebio.session import set_env, register_thread
from pywebio.io_ctrl import output_register_callback
from pywebio.output import close_popup


import json
import time
import os
import re
import threading
from datetime import datetime, timedelta


import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-face_recognition-thirdex")
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-unihiker_wifi-thirdex")
from unihiker import GUI
from unihiker_connet_wifi import *
from pinpong.board import Board,Pin
from pinpong.extension.unihiker import *
import siot
Board().begin()

from user_system import user_system
from medicine_countdown import reminder_manager
from medicine_check import check_time

id = 1
input_record = 0
saying = ['Enter medicine info','Add medicine info']
month_time = 'Every day'

#####################################################################################################################################################
                                                        # background countdown starter
def reminder_manager_start():
    # start background countdown
    reminder_manager.set_user_list()
    reminder_manager.is_running = True  # set running flag
    # register thread in session context
    reminder_thread = threading.Thread(target=reminder_manager.check_medicine_reminders, daemon=True)
    register_thread(reminder_thread)
    reminder_thread.start()

    reset_thread = threading.Thread(target=check_time, daemon=True)
    reset_thread.start()    

#####################################################################################################################################################
                                                        # webpage format
def page_show():
        # define banner style and title
        banner_html = """
        <div style="
            width: 100%;          /* width full screen */
            height: 80px;         /* banner height, can adjust as needed */
            background-color: #5E5EB3;  /* banner background color, light gray looks nicer */
            display: flex;        /* flex layout, for centering */
            align-items: center;  /* vertical center */
            justify-content: center;  /* horizontal center */
            border-radius: 4px;   /* slight rounded corners, nicer */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* slight shadow, better texture */
            margin-bottom: 20px;  /* spacing with content below */
        ">
            <h2 style="
                color: white;      /* text black */
                margin: 0;         /* clear default margin */
                font-size: 24px;   /* font size moderate, can adjust */
                font-weight: 600;  /* font bold, more eye-catching */
            ">Smart Medicine Box Control System</h2>
        </div>
        """
        small_rectangle = """
            <div style="
                width: 400px;          /* rectangle width */
                height: 50px;         /* rectangle height */
                background-color: #4CAF50;  /* rectangle background color (green) */
                border: 2px solid #388E3C;  /* border (dark green) */
                border-radius: 4px;    /* slight rounded corners */
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* slight shadow */
                margin: 10px 0;        /* spacing with elements above and below */
                display: flex;         /* flex layout, for centering content */
                align-items: center;   /* vertical center */
                justify-content: center; /* horizontal center */
                color: white;          /* text color */
                font-weight: bold;     /* text bold */
            ">User Settings</div>
            """      
        # output banner to webpage 
        put_html(banner_html)
        put_html(small_rectangle)
def face_page_show():
        # define banner style and title
        banner_html = """
        <div style="
            width: 100%;          /* width full screen */
            height: 80px;         /* banner height, can adjust as needed */
            background-color: #5E5EB3;  /* banner background color, light gray looks nicer */
            display: flex;        /* flex layout, for centering */
            align-items: center;  /* vertical center */
            justify-content: center;  /* horizontal center */
            border-radius: 4px;   /* slight rounded corners, nicer */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* slight shadow, better texture */
            margin-bottom: 20px;  /* spacing with content below */
        ">
            <h2 style="
                color: white;      /* text black */
                margin: 0;         /* clear default margin */
                font-size: 24px;   /* font size moderate, can adjust */
                font-weight: 600;  /* font bold, more eye-catching */
            ">Smart Medicine Box Control System</h2>
        </div>
        """
        small_rectangle = """
            <div style="
                width: 400px;          /* rectangle width */
                height: 50px;         /* rectangle height */
                background-color: #4CAF50;  /* rectangle background color (green) */
                border: 2px solid #388E3C;  /* border (dark green) */
                border-radius: 4px;    /* slight rounded corners */
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* slight shadow */
                margin: 10px 0;        /* spacing with elements above and below */
                display: flex;         /* flex layout, for centering content */
                align-items: center;   /* vertical center */
                justify-content: center; /* horizontal center */
                color: white;          /* text color */
                font-weight: bold;     /* text bold */
            ">Face Recognition in Progress</div>
            """      
        # output banner to webpage 
        put_html(banner_html)
        put_html(small_rectangle)
        
##################################################################################################################################################
                                                             # user system menu
def check_choice(x):
    try:
        if int(x) in [1,2,3,4]:
            return None
    except ValueError:
        return "Please enter correct operation number"
def user_system_menu():
    logged_user = None
    set_env(title="Smart Medicine Box Control System")
    with use_scope('user_system',clear=True):   
        page_show()
        put_text("User system started, you can register or login here") 
        reminder_manager_start()
        while True:
            all_user_list = us.user_list
            with use_scope('user_list',clear=True):
                put_table([[u.id,u.name,u.age,u.sex] for u in all_user_list],header=['ID','Username','Age','Gender'])
            choice = int(input("Please enter operation number:",placeholder="Please select operation: 1.Add user 2.Delete user 3.Modify user 4.Login 5.Exit",validate=check_choice))
            if choice == 1:
                us.add_user()
            elif choice == 2:
                us.delete_user()
            elif choice == 3:
                us.modify_user()
            elif choice == 4:
                logged_user = us.login()
                if logged_user is not None:
                    put_text(f"Welcome user {logged_user.name}")
                    time.sleep(1)
                    break
            elif choice == 5:
                put_text("Exited user system")
                break
            else:
                put_text("Input error, please re-enter")
    with use_scope('user_system',clear=True):
        pass
    if logged_user is not None:
        if not logged_user.face_data:
            face_page_show()
            siot.publish(topic="topic/a", data=f"face_data_load_request,id={logged_user.id}")
            logged_user.face_data = 1
            us.save_data()
            result = actions(label='Face Recognition', buttons=['Finish Recording'])
            if result == 'Finish Recording':
                logged_user.main_work(user_system_menu)
        else:
            logged_user.main_work(user_system_menu)

    elif logged_user is None:
        put_text("Not logged in, cannot perform operation")
        
###################################################################################################################################################
                                                            # MQTT
connection = False
def on_message_callback(client, userdata, msg):
    print(msg.payload.decode())
    if (msg.payload.decode().find("startup")!=-1):
        siot.publish(topic="topic/a", data="received")
        global connection
        connection = True
    if (msg.payload.decode().find("face_recognize_request")!=-1):
        msg = msg.payload.decode()
        # two groups
        user_id = re.search(r'(\d+)',msg)
        medicine_information = re.search(r'\((.*?)\).*\((.*?)\)', msg)
        medicine_name = medicine_information.group(1)
        medicine_time = medicine_information.group(2)
        print(f'medicine_name = {medicine_name},medicine_time = {medicine_time}')
        us.load_data()
        for user in us.user_list:
            for medicine in user.medicine_list:
                if medicine.m_name == medicine_name:
                    print(f'medicine_name {medicine.m_name}')
                    us.update_data(user_name=user.name,m_name = medicine_name,m_time = medicine_time)


def MQTT_init():
    siot.init(client_id="4637164937641405",server="192.168.123.1",port=1883,user="siot",password="dfrobot")
    siot.connect()
    siot.loop()
    siot.set_callback(on_message_callback)
    siot.getsubscribe(topic="topic/a")
    # while not connection:
    #     pass
    return True
##################################################################################################################################################
                                                        # main program
print('program start...')
u_gui=GUI()
u_gui.draw_text(text="Starting...",x=0,y=0,font_size=20, color="#0000FF")
while not MQTT_init():
    pass
print('MQTT_init over')
wifi_manager = WiFiManager()
response_success = wifi_manager.connect_wifi("yzh", "yzh12345")

while not (wifi_manager.is_wifi_connected()):
    pass
us = user_system()
start_server(user_system_menu, port=7878)
##################################################################################################################################################

