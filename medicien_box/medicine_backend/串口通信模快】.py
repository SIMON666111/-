import serial
import time
from unihiker import GUI  # 导入行空板屏幕控制库


# 串口配置
SERIAL_PORT = "/dev/ttyUSB0"  # 替换为你的端口
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # 等待Arduino初始化

    # 发送指令 + 屏幕显示回传（修复draw_rect参数）
    def send_and_show_on_screen(cmd):
        # 1. 发送指令
        ser.write(cmd)  # 简化写法，cmd本身就是字节（b'o'/b'c'）
        time.sleep(0.2)         # 等待Arduino回传
        # 2. 读取回传（增加空值判断，避免报错）
        response = ser.readline().decode().strip() if ser.in_waiting > 0 else "无响应"
        # 终端也同步显示（方便调试）
        print(f"发送：{cmd.decode()} | 回传：{response}")

    # 测试：发送o/c并显示
    send_and_show_on_screen(b'o')
    time.sleep(2)  # 停留2秒看效果
    send_and_show_on_screen(b'c')

except serial.SerialException as e:
    # 屏幕显示错误信息（修复坐标，避免重叠）
    print(f"串口失败：{e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print('close')