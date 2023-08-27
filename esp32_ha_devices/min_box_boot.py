'''
Author: cuipu g050505@gmail.com
Date: 2023-08-25 12:27:28
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-08-25 12:28:25
FilePath: \esp32_projects\esp32_ha_devices\min_box_boot.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from min_box import MinBox
import sys
import time
import machine



def main():
    try:
        min_box = MinBox()
        min_box.do_work()
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
    
    
