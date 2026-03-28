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
                                                             # user system
class user_system:                                           # user system
    def __init__(self):                                      # init user system
        self.user_list = []
        self.load_data() 
    def check_name(self,name):
        for user in self.user_list:
            if user.name == name:
                return "username already exists"
        return None
    def load_data(self):
        """load data from file"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()  # read and strip whitespace
                if not content:  # if file is empty
                    self.user_list = []
                else:
                    data = json.loads(content)  # use loads to parse string
                    self.user_list = [user(d['name'], d['age'], d['sex'], d['id'], d['face_data']) for d in data]
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            # catch all exceptions to make sure program doesn't crash
            self.user_list = []
            print(f"load data failed: {e}")  # print error info for debugging
    def save_data(self):
        """save data to file"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            data = []
            for u in self.user_list:
                data.append({'name': u.name, 'age': u.age, 'sex': u.sex,'id':u.id,'face_data':u.face_data})
            json.dump(data, f, ensure_ascii=False, indent=2)   
    def add_user(self):     
        try:              
            self.load_data()                     # add user       
            name = input("Please enter username:",validate=self.check_name)
            if name == None:
                return       
            age = int(input("Please enter user age:"))
            sex = select("Please select user gender:",options=['Male','Female'])
            next_id = max([u.id for u in self.user_list] or [0]) + 1
            user_in = user(name, age, sex, next_id, None)
            self.user_list.append(user_in)
            self.save_data()
            put_text("User added successfully")
        except Exception as e:
            put_text(f"Add user failed: {e}")
    def delete_user(self):                                 # delete user       
        try:
            self.load_data()
            name = input("Please enter username to delete:")
            for user in self.user_list:
                if user.name == name:
                    self.user_list.remove(user)
                    put_text("User deleted successfully")
                    self.save_data()
                    return
            put_text("User not found")
        except Exception as e:
            put_text(f"Delete user failed: {e}")     
    def modify_user(self):  
        self.load_data()                               # modify user                                   
        name = input("Please enter username:")
        for user in self.user_list:
            if user.name == name:
                age = int(input("Please enter user age:"))
                sex = select("Please select user gender:",options=['Male','Female'])
                user.age = age
                user.sex = sex
                self.save_data()
                put_text("User modified successfully")
                return
        put_text("User not found")
    def login(self):                                         # login user
        self.load_data()
        name = input("Please enter username:")
        for user in self.user_list:
            if user.name == name:
                put_text("Login successful")
                return user
        put_text("User not found")
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
