'''
Author: cuipu g050505@gmail.com
Date: 2023-05-19 23:47:11
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-24 18:52:12
FilePath: \esp32_projects\esp32_cam\boot.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()
from c_esp32_cam import ESP32Cam
import sys
import uerrno
import time
import machine

CLIENT_IP = '192.168.2.10'
CLIENT_PORT = 9000

def main():
    try:
        esp32_cam = ESP32Cam()
        # timer = Timer(1)  # 创建定时器对象
        # 定时器触发
        #esp32_cam.led_blink_timed(timer, 4, state='INIT')
        # esp32_cam.show_cam_init()
        esp32_cam.app.run(debug=True) # 因为 Web 服务器属于阻断式服务，如果写在下方将无法运行
        #esp32_cam.send_camera_feed(CLIENT_IP,CLIENT_PORT)
    except MemoryError:
        print("Memory error occurred. Restarting...")
    except OSError as e:
        error_code = e.args[0]
        error_name = uerrno.errorcode[error_code]
        print("OSError:", error_name)
    except Exception as e:
        print(f"Exception occurred: {e}")
        sys.print_exception(e)
    finally:
        time.sleep(10)
        # 重启设备
        machine.reset()


if __name__ == "__main__":  
    main()



