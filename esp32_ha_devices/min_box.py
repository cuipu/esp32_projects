'''
Author: cuipu g050505@gmail.com
Date: 2023-07-23 23:40:05
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-08-14 20:51:30
FilePath: \esp32_projects\esp32_ha_devices\min_box.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
from c_devices import ESP32160lcd,Ds18b20TemperatureSensor,LightSensorThreePin,InfraredMotionSensor,Relay
import sys
import time
import machine

# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()


ESP32160lcd_SCL_PIN = 22
ESP32160lcd_SDA_PIN = 21

#温度传感器
Ds18b20TemperatureSensor_PIN = 16

#光敏传感器
LightSensor_PIN = 17

# 红外人体感应
InfraredMotionSensor_PIN = 34

# 继电器
Relay_PIN = 19

class MinBox():
    def __init__(self):
        self.c_ESP32160lcd = ESP32160lcd(ESP32160lcd_SDA_PIN,ESP32160lcd_SCL_PIN)
        self.c_Ds18b20TemperatureSensor = Ds18b20TemperatureSensor(Ds18b20TemperatureSensor_PIN)
        self.c_LightSensorThreePin = LightSensorThreePin(LightSensor_PIN)
        self.c_InfraredMotionSensor= InfraredMotionSensor(InfraredMotionSensor_PIN)
        self.c_InfraredMotionSensor.set_hander(self.infraredMotionSensor_hander)
        self.c_Relay = Relay(Relay_PIN)

    def do_work(self):
        while(True):
            self.device, self.temp = self.c_Ds18b20TemperatureSensor.collect_temperature_result()
            self.light_digital = self.c_LightSensorThreePin.read_light_digital()
            print(self.temp)
            self.is_motion_detected = self.c_InfraredMotionSensor.is_motion_detected()
            print(self.is_motion_detected)
            self.c_ESP32160lcd.clear_msg()
            self.c_ESP32160lcd.show_msg("Temp: " + str(self.temp),str(self.is_motion_detected) + " " + str(self.light_digital))
            time.sleep(1)
            self.c_ESP32160lcd.clear_msg()

    def infraredMotionSensor_hander(self,*arges):
        if "0" == self.light_digital:
            print("light_digital: " + self.light_digital)
            return
        else:
            self.c_Relay.on()
            for i in range(5):
                self.c_ESP32160lcd.clear_msg()
                self.c_ESP32160lcd.show_msg("Temp: " + str(self.temp),"Light: on")
                time.sleep(1)
                self.c_ESP32160lcd.clear_msg()
            self.c_Relay.off()
            self.c_ESP32160lcd.show_msg("Temp: " + str(self.temp),"Light: off")

'''
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
'''
