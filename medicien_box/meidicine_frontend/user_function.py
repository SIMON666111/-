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
# constants
DATA_FILE_MEDICINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'medicine.json')
# variables
id = 1
input_record = 0
saying = ['Enter medicine info','Add medicine info']

menu = None
##################################################################################################################################
                                                       # medicine info input related functions
def check_input(value):
    try:
        int(value)
        return None
    except ValueError:
        return 'Please enter a number'
def check_dosage(dosage):
    try:
        int(dosage)
        return None
    except ValueError:
        return 'Please enter a number'
def time_input(time_list):
    put_text('Please drag the slider to enter medicine time')
    hour = slider('Hour', min=0, max=24, step=1, value=12)
    minute = slider('Minute', min=0, max=59, step=1, value=0)
    time_end = f"{hour}:{minute}" 
    put_text(f"The time you entered is: {time_end}")   
    time_list.append(time_end)
    return time_list
def time_list_input(dosage = 1):
    dosage = int(dosage)
    put_text(f"The dosage you entered is: {dosage}")
    time_list=[]
    if dosage > 1:
        i = 1
        while(i <= dosage):
            time_list = time_input(time_list)
            i += 1
    else:
        time_list = time_input(time_list)
    return time_list
def check_rl(rl):
    try:
        int(rl)
        return None
    except ValueError:
        return 'Please enter a number'
###################################################################################################################################################
                                                        # medicine info class
class medicine:
    def __init__(self, m_name,time_list, dosage,user_name,reserve_location,es = False):
        self.user_name = user_name
        self.m_name = m_name
        self.time_list = time_list
        self.dosage = dosage
        self.rl = reserve_location
        self.eat_state = es
        
    def get_countdown(self):
        """calculate countdown to next medicine time"""
        try:
            # extract medicine time from time_end, format: "Daily medicine time: HH:MM Monthly medicine times: X"
            import re
            time_end_list=[]
            for time_end in self.time_list:
                time_match = re.search(r'(\d+):(\d+)', time_end)
                if not time_match:
                    return "time format error"
                target_hour = int(time_match.group(1))
                target_minute = int(time_match.group(2))
                # get current time
                now = datetime.now()
                target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                
                # if target time has passed, set to tomorrow
                if target_time < now:
                    target_time += timedelta(days=1)
                
                # calculate time difference
                diff = target_time - now
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                time_end_list.append(f"{hours} hours {minutes} minutes")
            return time_end_list
        except Exception as e:
            return f"calculation error: {str(e)}"
########################################################################################################################################################
                                                       # user class and user frontend page
class user:
    # user class, contains user info and medicine list
    def __init__(self, name, age, sex, user_id,face_data=None):
        self.name = name
        self.age = age
        self.sex = sex
        self.id = user_id  # use passed id
        self.medicine_list = []
        self.face_data = face_data
        self.medicine_load()
    ##########################################################################################################################
    def medicine_load(self): # load medicine info
        self.medicine_list = []  # clear list first
        try:
            with open(DATA_FILE_MEDICINE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    self.medicine_list = []
                else:
                    data = json.loads(content)
                    for d in data:
                        if d['user_name'] == self.name:
                            self.medicine_list.append(medicine(d['m_name'], d['time_list'], d['dosage'],d['user_name'],d['rl'],d['eat_state']))    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.medicine_list = []
    def medicine_save(self): # save medicine info
        # first read existing data, keep other users' medicine info
        all_medicine = []
        try:
            print('save start')
            with open(DATA_FILE_MEDICINE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    all_medicine = json.loads(content)
                    # throw away current user's old data 
                    all_medicine = [d for d in all_medicine if d['user_name'] != self.name]
        except (FileNotFoundError, json.JSONDecodeError):
            all_medicine = []    
        # add current user's medicine data
        current_user_medicine = [{'m_name': m.m_name, 'time_list': m.time_list, 'dosage': m.dosage,'user_name':m.user_name,'eat_state':m.eat_state,'rl':m.rl} for m in self.medicine_list]
        all_medicine.extend(current_user_medicine)
        # write to file
        with open(DATA_FILE_MEDICINE, 'w', encoding='utf-8') as f:
            json.dump(all_medicine, f, ensure_ascii=False, indent=2)
    ##########################################################################################################################
    def in_input(self): # load user data
        self.medicine_load()
        with use_scope('medcine_input',clear=True):
            m_name = input('Please enter medicine type')
            put_text(f"The type you entered is: {m_name}")      
            for m in self.medicine_list:
                if m.m_name == m_name:
                    put_text(f'Medicine {m_name} already exists')
                    break
            else:
                dosage = int(input('Please enter medicine dosage',validate=check_dosage))
                time_list = time_list_input(dosage)
                reserve_location = input('Please enter storage location',validate=check_rl)
                clear()
                medicine_in = medicine(m_name,time_list,dosage,self.name,reserve_location,es=False)
                self.medicine_list.append(medicine_in)
                global input_record
                input_record = 1

        clear()
        self.medicine_save()
        self.main_work(menu)
    ##########################################################################################################################
    def modify_medicine_list(self): # modify medicine data
        self.medicine_load()
        medicine_name = input('Please enter medicine name to modify')
        modify_choice = select(label='Please select operation',options=[('Delete medicine','delete'),('Modify medicine','modify')])
        with use_scope('modify_medicine',clear=True):
            if modify_choice == 'delete':
                for m in self.medicine_list:
                    if m.m_name == medicine_name:
                        self.medicine_list.remove(m)
                        put_text(f'Medicine {medicine_name} deleted')
                        break
                else:
                    put_text(f'Medicine {medicine_name} not found')
            elif modify_choice == 'modify':
                for m in self.medicine_list:
                    if m.m_name == medicine_name:
                        modify_choice = select(label='Please select operation',options=[('Modify medicine type','modify_m_name'),('Modify medicine time','modify_time_list'),('Modify storage location','modify_reserve_location'),('Modify medicine dosage','modify_dosage')])
                        if modify_choice == 'modify_m_name':
                            m.m_name = input('Please enter new medicine type')
                            put_text(f'The new medicine type you entered is: {m.m_name}')
                        elif modify_choice == 'modify_time_list':
                            if m.dosage > 1:
                                time_num = input('Which time to modify?',validate=check_dosage)
                                time_num =int(time_num)
                                put_text('Please drag the slider to modify new medicine time')
                                hour = slider('Hour', min=0, max=24, step=1, value=12)
                                minute = slider('Minute', min=0, max=59, step=1, value=0)
                                time_end = f"{hour}:{minute}" 
                                put_text(f"The time you entered is: {time_end}")   
                                m.time_list[time_num - 1] = time_end
                            else:
                                m.time_list = time_list_input()
                        elif modify_choice == 'modify_dosage':
                            modify_choice = input('Add or delete')
                            if modify_choice == 'Add':
                                modify_num = int(input('Add how many times'))
                                modify_time_list = time_list_input(modify_num)
                                m.time_list.extend(modify_time_list)
                            else:
                                modify_num = int(input('Delete which time'))
                                del m.time_list[modify_num - 1]
                                print('delete successful')      
                        elif modify_choice == 'modify_reserve_location':
                            rl = input('Please enter new storage location',validate=check_rl)
                            m.rl = rl
        clear()
        self.medicine_save()
        self.main_work(menu)
    #################################################################################################################################
    def main_work(self,system_menu):    # frontend page display      
        global menu
        menu = system_menu
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
            ">Scheduled Medicine</div>
            """      
        # output banner to webpage 
        put_html(banner_html)
        put_button('User Settings', onclick=lambda: [clear(),menu()])
        put_html(small_rectangle)
        with use_scope('medicine_table',clear=True):
            self.medicine_load()
            put_table([[m.m_name,m.time_list,m.dosage,m.get_countdown(),m.eat_state,m.rl] for m in self.medicine_list],header=['Medicine Type','Medicine Time','Medicine Dosage','Countdown','Medicine Status','Storage Location'])
        put_text('Please enter medicine info')
        with use_scope('medcine_button',clear=True):
            put_button(saying[input_record], onclick=lambda: self.in_input())
            if self.medicine_list:
                put_button('Modify Medicine Info', onclick=lambda: self.modify_medicine_list())
            # custom button style, use registered callback function
        
