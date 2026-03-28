from medicine_face_recognize import face_recognition
face_system = face_recognition()
# unihiker board module
import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-unihiker_wifi-thirdex")
from unihiker import GUI
from unihiker_connet_wifi import *
from pinpong.extension.unihiker import *
from pinpong.board import Board,Pin
import siot
import re
import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"  # replace with your port
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

callback_enable = True
connection = False
def id_get(msg):
    user_id = re.search(r'(\d+)',msg)
    print(f'msg = {msg},user_id = {user_id}')
    if user_id:
        return user_id.group(1)
# event callback function
def on_message_callback(client, userdata, msg):
    print(msg.payload.decode())
    if msg.payload.decode().find("received")!=-1:
        siot.publish(topic="topic/a", data="done")
        global connection
        connection = True
    if msg.payload.decode().find("face_recognize_request")!=-1 and 'back' not in msg.payload.decode():
        user_id = id_get(msg.payload.decode())
        if face_system.face_recognition(user_id):
            rl = re.search(r'\((.*?)\).*\((.*?)\).*\((.*?)\)', msg)
            cmd = rl.group(3)
            if cmd == '1':send(b'1')
            elif cmd == '2':send(b'2')
            siot.publish(topic="topic/a", data=f'{msg.payload.decode()},back')
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
        siot.publish(topic="topic/a", data="startup")
        time.sleep(2)
    return True
# ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
def ser_init():
    try:
        time.sleep(2)  # wait for arduino init
        # 1. send command
        cmd = b'i'
        ser.write(cmd)  # simplified, cmd is bytes already (b'o'/b'c')
        time.sleep(0.5)         # wait for arduino response
        # 2. read response (add null check to avoid error)
        response = ser.readline().decode().strip() if ser.in_waiting > 0 else "no response"
        # also show in terminal (for debugging)
        print(f"send：{cmd.decode()} | response：{response}")
        if response == 'sure':
            return True
    except serial.SerialException as e:
        # screen shows error info (fix coordinates, avoid overlap)
        print(f"serial failed：{e}")
def ser_send(cmd):
    ser.write(cmd)
    response = ser.readline().decode().strip() if ser.in_waiting > 0 else "no response"
    print(f'reply：{response}')

print('program start...vv jjjj')
while not MQTT_init():
    pass
ser_init()
time.sleep(1)
print('connection was built')




