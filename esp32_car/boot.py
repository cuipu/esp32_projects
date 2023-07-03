'''
Author: cuipu g050505@gmail.com
Date: 2023-05-06 19:35:50
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-07-03 22:32:48
FilePath: \esp32_projects\esp32_car\boot.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
from c_car import CarController
import sys
import uerrno
import time
import machine


# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()


def main():
    try:
        car_controller = CarController()
        car_controller.do_work()
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
