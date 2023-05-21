'''
Author: cuipu g050505@gmail.com
Date: 2023-05-19 23:47:11
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-21 01:17:07
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

CLIENT_IP = '192.168.2.10'
CLIENT_PORT = 9000

def main():
    try:
        esp32_cam = ESP32Cam()
        esp32_cam.flash_led()
        esp32_cam.send_camera_feed(CLIENT_IP,CLIENT_PORT)
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
        print('system exit')
        sys.exit()


if __name__ == "__main__":
    main()
