'''
Author: cuipu g050505@gmail.com
Date: 2023-05-06 19:35:50
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-12 15:05:55
FilePath: \esp32_projects\my_ha_devices\boot.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
from c_home_assistant_devices import HASwitchDevice, HATemperatureSensor
import sys

# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()


def main():
    try:
        # ha_temperature_sensor = HATemperatureSensor()
        # ha_temperature_sensor.multi_thread_start_device()

        ha_relay = HASwitchDevice()
        ha_relay.start_device()
    except OSError as e:
        error_code = e.args[0]
        error_name = uerrno.errorcode[error_code]
        print("OSError:", error_name)
    except Exception as e:
        print(e)
    finally:
        sys.exit()


if __name__ == "__main__":
    main()
