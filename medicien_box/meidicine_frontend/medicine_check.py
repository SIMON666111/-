from datetime import datetime
import time
from user_system import user_system
us = user_system()

last_update_time = None

def update_eat_state():
    try:
        us.load_data()
        for user in us.user_list:
            for medicine in user.medicine_list:
                medicine.eat_state = False
        print('over')
        us.update_data(if_all = True)
    except Exception as e:
        print(f'重置出错:{e}')
def check_time(): 
    global last_update_time
    while True:
        now_time = datetime.now()
        if now_time.date() != last_update_time:
           
            last_update_time = now_time.date()
            update_eat_state()
        time.sleep(3600)

    