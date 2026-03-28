from medicine_face_recognize import face_recognition
face_system = face_recognition()
import re

def id_get(msg):
    user_id = re.search(r'(\d+)',msg)
    print(f'msg = {msg},user_id = {user_id}')
    if user_id:
        return user_id.group(1)
id = 1
say = f"face_data_load_request,id={id}"
user_id = id_get(say)
print(user_id)
if face_system.recognize_face(user_id)
