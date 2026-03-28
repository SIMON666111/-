from medicine_face_recognize import face_recognition
face_system = face_recognition()
#行空板模块
import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-unihiker_wifi-thirdex")
from unihiker import GUI
from unihiker_connet_wifi import *
from pinpong.extension.unihiker import *
from pinpong.board import Board,Pin
import siot
import re

callback_enable =True
connection = False
def id_get(msg):
    user_id = re.search(r'(\d+)',msg)
    print(f'msg = {msg},user_id = {user_id}')
    if user_id:
        return user_id.group(1)
# 事件回调函数
def on_message_callback(client, userdata, msg):
    print(msg.payload.decode())
    if msg.payload.decode().find("收到")!=-1:
        siot.publish(topic="topic/a", data="完成")
        global connection
        connection = True
    if msg.payload.decode().find("face_recognize_request")!=-1:
        user_id = id_get(msg.payload.decode())
        if face_system.face_recognition(user_id):
            print('pass')
        else:
            print('wrong')
        print('over')
        siot.publish(topic="topic/a", data="over")
    if msg.payload.decode().find('face_data_load_request')!=-1:
        user_id = id_get(msg.payload.decode())
        face_system.append_face_data(user_id)
        print('load over')
        

def MQTT_init():
    wifi_manager = WiFiManager()
    response_success = wifi_manager.connect_wifi("PB542477", "94587343")
    while not (wifi_manager.is_wifi_connected()):
        pass
    siot.init(client_id="03603899599931726",server="192.168.123.1",port=1883,user="siot",password="dfrobot")
    siot.connect()
    siot.loop()
    siot.set_callback(on_message_callback)
    siot.getsubscribe(topic="topic/a")
    while not connection:
        siot.publish(topic="topic/a", data="启动")
        time.sleep(2)
    return True

print('program start...vv jjjj')
while not MQTT_init():
    pass
print('connection was built')



