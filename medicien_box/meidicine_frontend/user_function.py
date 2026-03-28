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
month_time = '每天'
menu = None
##################################################################################################################################
                                                       #药物信息输入相关函数
def check_input(value):
    try:
        int(value)
        return None
    except ValueError:
        return '请输入一个数字'

def in_choice():
    with use_scope('month_if',clear=True):
        a = input('请输入每月用药量',validate=check_input)
        global month_time
        month_time = int(a)

def in_cancel():
    with use_scope('month_if',clear=True):
        put_text('请继续填写剩余内容')
        global month_time
        month_time = '每天'
###################################################################################################################################################
                                                        #药物信息类
class medicine:
    def __init__(self, m_name, time_end, dosage,user_name):
        self.user_name = user_name
        self.m_name = m_name
        self.time_end = time_end
        self.dosage = dosage
    
    def get_countdown(self):
        """计算距离下次用药的倒计时"""
        try:
            # 从 time_end 中提取用药时间，格式: " 每日用药时间：HH:MM 每月用药次数：X"
            import re
            time_match = re.search(r'(\d+):(\d+)', self.time_end)
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
            
            return f"{hours}小时{minutes}分钟"
        except Exception as e:
            return f"计算错误: {str(e)}"
########################################################################################################################################################
                                                       #用户类与用户前端页面
class user:
    # 用户类，包含用户信息和用药列表
    def __init__(self, name, age, sex, user_id, face_data=None):
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
                            self.medicine_list.append(medicine(d['m_name'], d['time_end'], d['dosage'],d['user_name']))    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.medicine_list = []
    def medicine_save(self): #药物信息保存
            # 先读取现有数据，保留其他用户的药物信息
        all_medicine = []
        try:
            with open(DATA_FILE_MEDICINE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    all_medicine = json.loads(content)
                    # 过滤掉当前用户的旧数据
                    all_medicine = [d for d in all_medicine if d['user_name'] != self.name]
        except (FileNotFoundError, json.JSONDecodeError):
            all_medicine = []    
        # 添加当前用户的药物数据
        current_user_medicine = [{'m_name': m.m_name, 'time_end': m.time_end, 'dosage': m.dosage,'user_name':m.user_name} for m in self.medicine_list]
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
                with use_scope('month_if',clear=True):
                    put_text('设置每月用药量，若取消则默认一天一次')
                    choice = actions('请选择', ['确认','取消'])
                    if choice == '确认':
                        in_choice()
                    elif choice == '取消':
                        in_cancel()
                put_text('请拖动圆点来输入用药时间')
                hour = slider('时', min=0, max=24, step=1, value=12)
                minute = slider('分', min=0, max=59, step=1, value=0)
                time = f"{hour}:{minute}"
                time_end = f" 每日用药时间：{time} 每月用药次数：{month_time}"
                put_text(f"你输入的时间是：{time_end}")   
                dosage = input('请输入用药剂量')
                put_text(f"你输入的剂量是：{dosage}")
                clear()
                
                medicine_in = medicine(m_name,time_end,dosage,self.name)
                self.medicine_list.append(medicine_in)
                global input_record
                input_record = 1
                with use_scope('medcine_button',clear=True):
                    put_button(saying[input_record], onclick=lambda: self.in_input())
                with use_scope('medicine_table',clear=True):
                    put_table([[m.m_name,m.time_end,m.dosage,m.get_countdown()] for m in self.medicine_list],header=['用药种类','用药时间','用药剂量','倒计时'])
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
                        modify_choice = select(label='请选择操作',options=[('修改用药种类','modify_m_name'),('修改用药时间','modify_time_end'),('修改用药剂量','modify_dosage')])
                        if modify_choice == 'modify_m_name':
                            m.m_name = input('请输入新的用药种类')
                            put_text(f'你输入的新的用药种类是：{m.m_name}')
                        elif modify_choice == 'modify_time_end':
                            with use_scope('month_if',clear=True):
                                put_text('设置每月用药量，若取消则默认一天一次')
                                choice = actions('请选择', ['确认','取消'])
                                if choice == '确认':
                                    in_choice()
                                elif choice == '取消':
                                    in_cancel()
                            put_text('请拖动圆点来输入用药时间')
                            hour = slider('时', min=0, max=24, step=1, value=12)
                            minute = slider('分', min=0, max=60, step=1, value=0)
                            time = f"{hour}:{minute}"
                            time_end = f" 每日用药时间：{time} 每月用药次数：{month_time}"
                            put_text(f"你输入的时间是：{time_end}")   
                            m.time_end = time_end
                        elif modify_choice == 'modify_dosage':
                            m.dosage = input('请输入新的用药剂量')
                            put_text(f'你输入的新的用药剂量是：{m.dosage}')
        clear()
        self.medicine_save()
        self.main_work(menu)
    #################################################################################################################################
   def _show_page_header(self):
        """显示页面头部（横幅）"""
        banner_html = """
        <div style="
            width: 100%;
            height: 80px;
            background-color: #5E5EB3;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
            <h2 style="
                color: white;
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            ">智能药箱控制系统</h2>
        </div>
        """
        put_html(banner_html)
    
    def _show_user_settings_button(self):
        """显示用户设置按钮和绿色长方形"""
        small_rectangle = """
        <div style="
            width: 400px;
            height: 50px;
            background-color: #4CAF50;
            border: 2px solid #388E3C;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        ">定时用药</div>
        """
        global menu
        put_button('用户设置', onclick=lambda: [clear(), menu()])
        put_html(small_rectangle)
    
    def _show_medicine_table(self):
        """显示用药信息表格"""
        with use_scope('medicine_table', clear=True):
            self.medicine_load()
            put_table(
                [[m.m_name, m.time_end, m.dosage, m.get_countdown()] for m in self.medicine_list],
                header=['用药种类', '用药时间', '用药剂量', '倒计时']
            )
    
    def _show_action_buttons(self):
        """显示操作按钮（添加/修改药物）"""
        global input_record, saying
        put_text('请输入用药信息')
        with use_scope('medcine_button', clear=True):
            put_button(saying[input_record], onclick=lambda: self.in_input())
            if self.medicine_list:
                put_button('修改药物信息', onclick=lambda: self.modify_medicine_list())
    
    def main_work(self, system_menu):
        """主页面"""
        global menu
        menu = system_menu
        
        # 显示页面头部
        self._show_page_header()
        
        # 显示用户设置按钮
        self._show_user_settings_button()
        
        # 显示用药表格
        self._show_medicine_table()
        
        # 显示操作按钮（添加/修改药物）
        self._show_action_buttons()
