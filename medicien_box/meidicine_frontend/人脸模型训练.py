#  -*- coding: UTF-8 -*-
"""
人脸识别训练程序
功能：
1. 初始化摄像头
2. 采集50张人脸照片
3. 训练LBPH人脸识别模型
4. 保存训练好的模型
"""

# MindPlus 环境配置
import sys
sys.path.append("/root/mindplus/.lib/thirdExtension/nick-face_recognition-thirdex")

import os
import datetime
import time
import cv2
import numpy as np
import train_model  # 自定义的训练模型模块

# 导入PIL库（用于绘制中文字符）
from PIL import Image, ImageDraw, ImageFont


def numberMap(x, in_min, in_max, out_min, out_max):
    """
    数值映射函数
    将一个范围的数值映射到另一个范围
    参数：
        x: 输入值
        in_min: 输入最小值
        in_max: 输入最大值
        out_min: 输出最小值
        out_max: 输出最大值
    返回：
        映射后的数值
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def drawChinese(text, x, y, size, r, g, b, a, img):
    """
    绘制中文字符函数
    参数：
        text: 要绘制的文字
        x, y: 绘制位置
        size: 字体大小
        r, g, b, a: 颜色值（RGBA）
        img: 要绘制的图像
    返回：
        绘制后的图像
    """
    font = ImageFont.truetype("HYQiHei_50S.ttf", size)  # 加载中文字体
    img_pil = Image.fromarray(img)  # 转换为PIL图像
    draw = ImageDraw.Draw(img_pil)  # 创建绘制对象
    draw.text((x, y), text, font=font, fill=(b, g, r, a))  # 绘制文字（注意颜色顺序是BGR）
    frame = np.array(img_pil)  # 转换回numpy数组
    return frame

id = 2  # 类别ID
# 摄像头初始化
cap = cv2.VideoCapture(0)  # 打开默认摄像头
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # 设置宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 设置高度
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 设置缓冲区大小
# 创建全屏窗口
cv2.namedWindow('cvwindow', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('cvwindow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# 计数器初始化
pic_counta = 0  # 照片计数器
pic_countb = 0  # 未使用的计数器
font = cv2.FONT_HERSHEY_SIMPLEX  # 字体

# 等待摄像头打开
while not cap.isOpened():
    continue

# 加载人脸检测器和识别器
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # 人脸检测分类器
recognizer = cv2.face.LBPHFaceRecognizer_create()  # LBPH人脸识别器


# 等待用户按下'a'键开始
while not (cv2.waitKey(10) == ord('a')):
    time.sleep(0.1)


# 采集50张人脸照片
while not (pic_counta >= 50):
    cvimg_success, img_src = cap.read()  # 读取摄像头画面
    if not cvimg_success:
        continue
        
    # 图像处理：裁剪和调整大小
    cvimg_h, cvimg_w, cvimg_c = img_src.shape
    cvimg_w1 = cvimg_h * 240 // 320  # 计算宽度（保持240:320的比例）
    cvimg_x1 = (cvimg_w - cvimg_w1) // 2  # 计算起始X坐标
    img_src = img_src[:, cvimg_x1:cvimg_x1 + cvimg_w1]  # 裁剪图像
    img_src = cv2.resize(img_src, (240, 320))  # 调整大小
    
    # 转换为灰度图（人脸检测需要）
    gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)

    if pic_counta < 50:  # 还没拍完50张
        cv2.putText(img_src, 'shooting', (10, 30), font, 0.8, (0, 255, 0), 2)
    # 检测人脸
    faces = detector.detectMultiScale(gray, 1.3, 5)  # 参数：图像，缩放因子，最小邻居数
    
    # 显示原始图像
    cv2.imshow('cvwindow', img_src)
    
    # 设置保存路径（类别id）
    img_dir_path = "/root/face_recognition/picture/" + str(id) + "/"
    img_name_path = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')) + ".jpg"  # 以时间戳命名
    img_save_path = img_dir_path + img_name_path
    
    # 检查并创建目录
    try:
        if not os.path.exists(img_dir_path):
            print("The folder does not exist, created automatically")
            os.system("mkdir -p /root/face_recognition/picture/" + str(id) + "/")  # 创建目录
    except IOError:
        print("IOError, created automatically")
        break
    
    # 处理检测到的人脸
    for (x, y, w, h) in faces:
        # 绘制人脸框
        cv2.rectangle(img_src, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # 保存照片
        if pic_counta <= 50:
            cv2.putText(img_src, 'shooting', (10, 50), font, 0.6, (0, 255, 0), 2)  # 显示"拍摄中"
            cv2.imwrite(img_save_path, img_src)  # 保存图像
            pic_counta += 1  # 计数器加1
            print("save picture path:", img_save_path)  # 打印保存路径
            print("save 0-picture count:" + str(pic_counta))  # 打印保存数量
            cv2.putText(img_src, '0', (x, y + h), font, 0.6, (0, 0, 255), 2)  # 显示类别标签
            time.sleep(0.05)  # 短暂暂停
        else:
            cv2.putText(img_src, 'Done, Please quit', (10, 50), font, 0.6, (0, 255, 0), 2)  # 显示"完成"
            time.sleep(2)
    
    # 显示处理后的图像
    cv2.imshow('cvwindow', img_src)
    cv2.waitKey(5)  # 等待5毫秒


# 释放摄像头资源
cap.release()
cv2.destroyAllWindows()


# 重新初始化检测器和识别器
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 训练模型
faces, Ids = train_model.get_images_and_labels('/root/face_recognition/picture/')  # 获取图像和标签
recognizer.train(faces, np.array(Ids))  # 训练模型

# 保存模型
img_dir_path = "/root/face_recognition/model/model.yml"
img_dir_path = os.path.abspath(os.path.dirname(img_dir_path))  # 获取目录路径
print(img_dir_path)

# 检查并创建目录
try:
    if not os.path.exists(img_dir_path):
        print("The folder does not exist, created automatically")
        os.mkdir(img_dir_path)  # 创建目录
except IOError:
    print("IOError, created automatically")

# 保存模型文件
recognizer.save("/root/face_recognition/model/model.yml")
print("模型训练完成并保存")