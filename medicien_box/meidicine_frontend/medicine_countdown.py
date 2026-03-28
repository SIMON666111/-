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
                                                        #后台倒计时管理器
class MedicineReminderManager:
    """后台倒计时提醒管理器"""
    def __init__(self):
        self.is_running = False
        self.reminder_thread = None
        self.user_list = []
    
    def set_user_list(self):
        """设置用户列表"""
        us.load_data()
        self.user_list = us.user_list
    
    def check_medicine_reminders(self):
        """检查并处理用药提醒"""
        while self.is_running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                us.load_data()
                self.user_list = us.user_list
                for user in self.user_list:
                    print('enter')
                    for medicine in user.medicine_list:
                        # 提取用药时间
                        time_match = re.search(r'(\d+):(\d+)', medicine.time_end)
                        if time_match:
                            target_time = f"{time_match.group(1)}:{time_match.group(2)}"                          
                            # 如果当前时间等于用药时间，触发提醒
                            if current_time == target_time:
                                # 这里可以添加提醒逻辑，比如弹窗、声音等
                                buzzer.pitch(131,16)
                                popup(f"提醒：用户 {user.name} 该服用 {medicine.m_name} 了！")
                                siot.publish(topic="topic/a", data=f"face_recognize_request,id={user.id}")
                                # 可以在这里添加 PyWebIO 的输出或其他提醒方式
                # 每分钟检查一次
                time.sleep(60)
            except Exception as e:
                print(f"倒计时检查出错：{e}")
                time.sleep(60)
    
    def start(self):
        """启动后台倒计时"""
        if not self.is_running:
            self.is_running = True
            print("后台倒计时已启动")
    
    def stop(self):
        """停止后台倒计时"""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join()
        print("后台倒计时已停止")

# 创建全局倒计时管理器
reminder_manager = MedicineReminderManager()
