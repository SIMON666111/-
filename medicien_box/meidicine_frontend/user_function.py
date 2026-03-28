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
#常量
DATA_FILE_MEDICINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'medicine.json')
#变量
id = 1
input_record = 0
saying = ['输入用药信息','添加用药信息']

menu = None
##################################################################################################################################
                                                       #药物信息输入相关函数
def check_input(value):
    try:
        int(value)
        return None
    except ValueError:
        return '请输入一个数字'
def check_dosage(dosage):
    try:
        int(dosage)
        return None
    except ValueError:
        return '请输入一个数字'
def time_input(time_list):
    put_text('请拖动圆点来输入用药时间')
    hour = slider('时', min=0, max=24, step=1, value=12)
    minute = slider('分', min=0, max=59, step=1, value=0)
    time_end = f"{hour}:{minute}" 
    put_text(f"你输入的时间是：{time_end}")   
    time_list.append(time_end)
    return time_list
def time_list_input(dosage = 1):
    dosage = int(dosage)
    put_text(f"你输入的剂量是：{dosage}")
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
        return '请输入一个数字'
###################################################################################################################################################
                                                        #药物信息类
class medicine:
    def __init__(self, m_name,time_list, dosage,user_name,reserve_location,es = False):
        self.user_name = user_name
        self.m_name = m_name
        self.time_list = time_list
        self.dosage = dosage
        self.rl = reserve_location
        self.eat_state = es
        
    def get_countdown(self):
        """计算距离下次用药的倒计时"""
        try:
            # 从 time_end 中提取用药时间，格式: " 每日用药时间：HH:MM 每月用药次数：X"
            import re
            time_end_list=[]
            for time_end in self.time_list:
                time_match = re.search(r'(\d+):(\d+)', time_end)
                if not time_match:
                    return "时间格式错误"
                target_hour = int(time_match.group(1))
                target_minute = int(time_match.group(2))
                # 获取当前时间
                now = datetime.now()
                target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                
                # 如果目标时间已经过了，设置为明天
                if target_time < now:
                    target_time += timedelta(days=1)
                
                # 计算时间差
                diff = target_time - now
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                time_end_list.append(f"{hours}小时{minutes}分钟")
            return time_end_list
        except Exception as e:
            return f"计算错误: {str(e)}"
########################################################################################################################################################
                                                       #用户类与用户前端页面
class user:
    # 用户类，包含用户信息和用药列表
    def __init__(self, name, age, sex, user_id,face_data=None):
        self.name = name
        self.age = age
        self.sex = sex
        self.id = user_id  # 使用传入的id
        self.medicine_list = []
        self.face_data = face_data
        self.medicine_load()
    ##########################################################################################################################
    def medicine_load(self):#药物信息加载
        self.medicine_list = []  # 先清空列表
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
    def medicine_save(self): #药物信息保存
        # 先读取现有数据，保留其他用户的药物信息
        all_medicine = []
        try:
            print('save start')
            with open(DATA_FILE_MEDICINE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    all_medicine = json.loads(content)
                    # 扔掉当前用户的旧数据 
                    all_medicine = [d for d in all_medicine if d['user_name'] != self.name]
        except (FileNotFoundError, json.JSONDecodeError):
            all_medicine = []    
        # 添加当前用户的药物数据
        current_user_medicine = [{'m_name': m.m_name, 'time_list': m.time_list, 'dosage': m.dosage,'user_name':m.user_name,'eat_state':m.eat_state,'rl':m.rl} for m in self.medicine_list]
        all_medicine.extend(current_user_medicine)
        # 写入文件
        with open(DATA_FILE_MEDICINE, 'w', encoding='utf-8') as f:
            json.dump(all_medicine, f, ensure_ascii=False, indent=2)
    ##########################################################################################################################
    def in_input(self): #用户数据载入
        self.medicine_load()
        with use_scope('medcine_input',clear=True):
            m_name = input('请输入用药种类')
            put_text(f"你输入的种类是：{m_name}")      
            for m in self.medicine_list:
                if m.m_name == m_name:
                    put_text(f'已存在药物{m_name}')
                    break
            else:
                dosage = int(input('请输入用药量剂',validate=check_dosage))
                time_list = time_list_input(dosage)
                reserve_location = input('请输入存放格数',validate=check_rl)
                clear()
                medicine_in = medicine(m_name,time_list,dosage,self.name,reserve_location,es=False)
                self.medicine_list.append(medicine_in)
                global input_record
                input_record = 1

        clear()
        self.medicine_save()
        self.main_work(menu)
    ##########################################################################################################################
    def modify_medicine_list(self): #药物数据修改
        self.medicine_load()
        medicine_name = input('请输入要修改的药物名称')
        modify_choice = select(label='请选择操作',options=[('删除药物','delete'),('修改药物','modify')])
        with use_scope('modify_medicine',clear=True):
            if modify_choice == 'delete':
                for m in self.medicine_list:
                    if m.m_name == medicine_name:
                        self.medicine_list.remove(m)
                        put_text(f'已删除药物{medicine_name}')
                        break
                else:
                    put_text(f'未找到药物{medicine_name}')
            elif modify_choice == 'modify':
                for m in self.medicine_list:
                    if m.m_name == medicine_name:
                        modify_choice = select(label='请选择操作',options=[('修改用药种类','modify_m_name'),('修改用药时间','modify_time_list'),('修改存放格数','modify_reserve_location')('修改用药剂量','modify_dosage')])
                        if modify_choice == 'modify_m_name':
                            m.m_name = input('请输入新的用药种类')
                            put_text(f'你输入的新的用药种类是：{m.m_name}')
                        elif modify_choice == 'modify_time_list':
                            if m.dosage > 1:
                                time_num = input('修改药物的第几次服用？',validate=check_dosage)
                                time_num =int(time_num)
                                put_text('请拖动圆点来修改新的用药时间')
                                hour = slider('时', min=0, max=24, step=1, value=12)
                                minute = slider('分', min=0, max=59, step=1, value=0)
                                time_end = f"{hour}:{minute}" 
                                put_text(f"你输入的时间是：{time_end}")   
                                m.time_list[time_num - 1] = time_end
                            else:
                                m.time_list = time_list_input()
                        elif modify_choice == 'modify_dosage':
                            modify_choice = input('增加或是删除')
                            if modify_choice == '增加':
                                modify_num = int(input('增加次数'))
                                modify_time_list = time_list_input(modify_num)
                                m.time_list.extend(modify_time_list)
                            else:
                                modify_num = int(input('删除第几次'))
                                del m.time_list[modify_num - 1]
                                print('删除成功')      
                        elif modify_choice == 'modify_reserve_location':
                            rl = input('请输入新的存放格数',validate=check_rl)
                            m.rl = rl
        clear()
        self.medicine_save()
        self.main_work(menu)
    #################################################################################################################################
    def main_work(self,system_menu):    #前端页面显示      
        global menu
        menu = system_menu
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
            ">定时用药</div>
            """      
        # 输出横幅到网页 
        put_html(banner_html)
        put_button('用户设置', onclick=lambda: [clear(),menu()])
        put_html(small_rectangle)
        with use_scope('medicine_table',clear=True):
            self.medicine_load()
            put_table([[m.m_name,m.time_list,m.dosage,m.get_countdown(),m.eat_state,m.rl] for m in self.medicine_list],header=['用药种类','用药时间','用药剂量','倒计时','用药状态','存放位置'])
        put_text('请输入用药信息')
        with use_scope('medcine_button',clear=True):
            put_button(saying[input_record], onclick=lambda: self.in_input())
            if self.medicine_list:
                put_button('修改药物信息', onclick=lambda: self.modify_medicine_list())
            # 自定义按钮样式，使用注册的回调函数
        