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
saying = ['输入用药信息','添加用药信息']
month_time = '每天'

#####################################################################################################################################################
                                                        #后台倒计时启动器
def reminder_manager_start():
    # 启动后台倒计时
    reminder_manager.set_user_list()
    reminder_manager.is_running = True  # 设置运行标志
    # 在有会话的上下文中注册线程
    reminder_thread = threading.Thread(target=reminder_manager.check_medicine_reminders, daemon=True)
    register_thread(reminder_thread)
    reminder_thread.start()

    reset_thread = threading.Thread(target=check_time, daemon=True)
    reset_thread.start()    

#####################################################################################################################################################
                                                        #网页格式
def page_show():
        # 定义横幅样式和标题
        banner_html = """
        <div style="
            width: 100%;          /* 宽度占满屏幕 */
            height: 80px;         /* 横幅高度，可根据需要调整 */
            background-color: #5E5EB3;  /* 横幅背景色，浅灰色更美观 */
            display: flex;        /* 弹性布局，用于居中 */
            align-items: center;  /* 垂直居中 */
            justify-content: center;  /* 水平居中 */
            border-radius: 4px;   /* 轻微圆角，更美观 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* 轻微阴影，提升质感 */
            margin-bottom: 20px;  /* 与下方内容的间距 */
        ">
            <h2 style="
                color: white;      /* 文字黑色 */
                margin: 0;         /* 清除默认边距 */
                font-size: 24px;   /* 字体大小适中，可调整 */
                font-weight: 600;  /* 字体加粗，更醒目 */
            ">智能药箱控制系统</h2>
        </div>
        """
        small_rectangle = """
            <div style="
                width: 400px;          /* 长方形宽度 */
                height: 50px;         /* 长方形高度 */
                background-color: #4CAF50;  /* 长方形背景色（绿色） */
                border: 2px solid #388E3C;  /* 边框（深绿色） */
                border-radius: 4px;    /* 轻微圆角 */
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* 轻微阴影 */
                margin: 10px 0;        /* 与上下元素的间距 */
                display: flex;         /* 弹性布局，用于居中内容 */
                align-items: center;   /* 垂直居中 */
                justify-content: center; /* 水平居中 */
                color: white;          /* 文字颜色 */
                font-weight: bold;     /* 文字加粗 */
            ">用户设置</div>
            """      
        # 输出横幅到网页 
        put_html(banner_html)
        put_html(small_rectangle)
def face_page_show():
        # 定义横幅样式和标题
        banner_html = """
        <div style="
            width: 100%;          /* 宽度占满屏幕 */
            height: 80px;         /* 横幅高度，可根据需要调整 */
            background-color: #5E5EB3;  /* 横幅背景色，浅灰色更美观 */
            display: flex;        /* 弹性布局，用于居中 */
            align-items: center;  /* 垂直居中 */
            justify-content: center;  /* 水平居中 */
            border-radius: 4px;   /* 轻微圆角，更美观 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* 轻微阴影，提升质感 */
            margin-bottom: 20px;  /* 与下方内容的间距 */
        ">
            <h2 style="
                color: white;      /* 文字黑色 */
                margin: 0;         /* 清除默认边距 */
                font-size: 24px;   /* 字体大小适中，可调整 */
                font-weight: 600;  /* 字体加粗，更醒目 */
            ">智能药箱控制系统</h2>
        </div>
        """
        small_rectangle = """
            <div style="
                width: 400px;          /* 长方形宽度 */
                height: 50px;         /* 长方形高度 */
                background-color: #4CAF50;  /* 长方形背景色（绿色） */
                border: 2px solid #388E3C;  /* 边框（深绿色） */
                border-radius: 4px;    /* 轻微圆角 */
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* 轻微阴影 */
                margin: 10px 0;        /* 与上下元素的间距 */
                display: flex;         /* 弹性布局，用于居中内容 */
                align-items: center;   /* 垂直居中 */
                justify-content: center; /* 水平居中 */
                color: white;          /* 文字颜色 */
                font-weight: bold;     /* 文字加粗 */
            ">正在进行人脸识别</div>
            """      
        # 输出横幅到网页 
        put_html(banner_html)
        put_html(small_rectangle)
        
##################################################################################################################################################
                                                             #用户系统菜单
def check_choice(x):
    try:
        if int(x) in [1,2,3,4]:
            return None
    except ValueError:
        return "请输入正确的操作编号"
def user_system_menu():
    logged_user = None
    set_env(title="智能药箱控制系统")
    with use_scope('user_system',clear=True):   
        page_show()
        put_text("用户系统已启动，你可以在这里注册或登陆账号") 
        reminder_manager_start()
        while True:
            all_user_list = us.user_list
            with use_scope('user_list',clear=True):
                put_table([[u.id,u.name,u.age,u.sex] for u in all_user_list],header=['ID','用户名','年龄','性别'])
            choice = int(input("请输入操作编号：",placeholder="请选择操作：1.添加用户 2.删除用户 3.修改用户 4.登陆账号 5.退出",validate=check_choice))
            if choice == 1:
                us.add_user()
            elif choice == 2:
                us.delete_user()
            elif choice == 3:
                us.modify_user()
            elif choice == 4:
                logged_user = us.login()
                if logged_user is not None:
                    put_text(f"欢迎用户 {logged_user.name}")
                    time.sleep(1)
                    break
            elif choice == 5:
                put_text("已退出用户系统")
                break
            else:
                put_text("输入错误，请重新输入")
    with use_scope('user_system',clear=True):
        pass
    if logged_user is not None:
        if not logged_user.face_data:
            face_page_show()
            siot.publish(topic="topic/a", data=f"face_data_load_request,id={logged_user.id}")
            logged_user.face_data = 1
            us.save_data()
            result = actions(label='人脸识别', buttons=['结束录入'])
            if resuit == '结束录入':
                logged_user.main_work(user_system_menu)
        else:
            logged_user.main_work(user_system_menu)

    elif logged_user is None:
        put_text("未登录用户，无法进行操作")
        
###################################################################################################################################################
                                                            #MQTT
connection = False
def on_message_callback(client, userdata, msg):
    print(msg.payload.decode())
    if (msg.payload.decode().find("启动")!=-1):
        siot.publish(topic="topic/a", data="收到")
        global connection
        connection = True
    if (msg.payload.decode().find("face_recognize_request")!=-1):
        msg = msg.payload.decode()
        # 两个分组
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
                                                        #主程序
print('program start...')
u_gui=GUI()
u_gui.draw_text(text="正在启动...",x=0,y=0,font_size=20, color="#0000FF")
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


