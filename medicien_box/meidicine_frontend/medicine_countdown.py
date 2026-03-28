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
us = user_system()
###################################################################################################################################################
                                                        # background countdown manager
class MedicineReminderManager:
    """background countdown reminder manager"""
    def __init__(self):
        self.is_running = False
        self.reminder_thread = None
        self.user_list = []
    
    def set_user_list(self):
        """set user list"""
        us.load_data()
        self.user_list = us.user_list
    
    def check_medicine_reminders(self):
        """check and handle medicine reminders"""
        while self.is_running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                if '0' in current_time:
                    hour, minute = current_time.split(':')
                    hour = str(int(hour))
                    minute = str(int(minute))
                    current_time = f'{hour}:{minute}'

                us.load_data()
                self.user_list = us.user_list
                for user in self.user_list:
                    print('enter')
                    for medicine in user.medicine_list:
                        # extract medicine time
                        print(f'enter {user.name} medicine_list')
                        i=1
                        for time_end in medicine.time_list:
                            
                            time_match = re.search(r'(\d+):(\d+)', time_end)
                            if time_match:
                                target_time = f"{time_match.group(1)}:{time_match.group(2)}"
                                print(f'enter_time_list,time = {target_time},now_time = {current_time}')                          
                                # if current time equals medicine time, trigger reminder
                                if current_time == target_time:
                                    print('on time')
                                    # here you can add reminder logic, like popup, sound, etc.
                                    buzzer.pitch(131,16)
                                    popup(f"Reminder: User {user.name} should take {medicine.m_name} now!")
                                    siot.publish(topic="topic/a", data=f"face_recognize_request,id={user.id},rl={medicine.rl},medicine_name=({medicine.m_name}),time=({i})")
                                # you can add PyWebIO output or other reminder methods here
                            i+=1
                # check once per minute
                time.sleep(60)
            except Exception as e:
                print(f"countdown check error: {e}")
                time.sleep(60)
    
    def start(self):
        """start background countdown"""
        if not self.is_running:
            self.is_running = True
            print("background countdown started")
    
    def stop(self):
        """stop background countdown"""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join()
        print("background countdown stopped")

# create global countdown manager
reminder_manager = MedicineReminderManager()
