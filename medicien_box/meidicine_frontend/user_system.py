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
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')
DATA_FILE_MEDICINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'medicine.json')
id = 1


from user_function import user
###########################################################################################################################################
                                                             #用户系统
class user_system:                                           #用户系统
    def __init__(self):                                      #初始化用户系统
        self.user_list = []
        self.load_data() 
    def check_name(self,name):
        for user in self.user_list:
            if user.name == name:
                return "用户名已存在"
        return None
    def load_data(self):
        """从文件加载数据"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()  # 读取并去除首尾空白
                if not content:  # 如果文件为空
                    self.user_list = []
                else:
                    data = json.loads(content)  # 使用loads解析字符串
                    self.user_list = [user(d['name'], d['age'], d['sex'], d['id'], d['face_data']) for d in data]
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            # 捕获所有异常，确保程序不会崩溃
            self.user_list = []
            print(f"加载数据失败：{e}")  # 打印错误信息，方便调试
    def save_data(self):
        """保存数据到文件"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            data = []
            for u in self.user_list:
                data.append({'name': u.name, 'age': u.age, 'sex': u.sex,'id':u.id,'face_data':u.face_data})
            json.dump(data, f, ensure_ascii=False, indent=2)   
    def add_user(self):     
        try:              
            self.load_data()                     # 添加用户       
            name = input("请输入用户名：",validate=self.check_name)
            if name == None:
                return       
            age = int(input("请输入用户年龄："))
            sex = select("请输入用户性别：",options=['男','女'])
            next_id = max([u.id for u in self.user_list] or [0]) + 1
            user_in = user(name, age, sex, next_id, None)
            self.user_list.append(user_in)
            self.save_data()
            put_text("用户添加成功")
        except Exception as e:
            put_text(f"添加用户失败：{e}")
    def delete_user(self):                                 #删除用户       
        try:
            self.load_data()
            name = input("请输入要删除的用户名：")
            for user in self.user_list:
                if user.name == name:
                    self.user_list.remove(user)
                    put_text("用户删除成功")
                    self.save_data()
                    return
            put_text("用户不存在")
        except Exception as e:
            put_text(f"删除用户失败：{e}")     
    def modify_user(self):  
        self.load_data()                               #修改用户                                   
        name = input("请输入用户名：")
        for user in self.user_list:
            if user.name == name:
                age = int(input("请输入用户年龄："))
                sex = select("请输入用户性别：",options=['男','女'])
                user.age = age
                user.sex = sex
                self.save_data()
                put_text("用户修改成功")
                return
        put_text("用户不存在")
    def login(self):                                         #登录用户
        self.load_data()
        name = input("请输入用户名：")
        for user in self.user_list:
            if user.name == name:
                put_text("登陆成功")
                return user
        put_text("用户不存在")
        return None
    def update_data(self,user_name = None,m_name=None,m_time=None,if_all = False):
        name = user_name
        self.load_data()
        if if_all:
            for user in self.user_list:
                for m in user.medicine_list: m.eat_state = False
                user.medicine_save()
            return None
        else:
            for user in self.user_list:
                if user.name == name:
                    print(user.name)
                    for m in user.medicine_list:
                        if m.m_name == m_name:
                            
                            user.medicine_save()
                            return None