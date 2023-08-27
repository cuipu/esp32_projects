'''
Author: cuipu g050505@gmail.com
Date: 2023-07-23 23:40:05
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-08-27 21:53:20
FilePath: \esp32_projects\esp32_ha_devices\min_box.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
from c_devices import ESP32160lcd,Ds18b20TemperatureSensor,LightSensorThreePin,InfraredMotionSensor,Relay
import sys
import time
import utime
import machine
from c_utils import WiFiUtil,TimeUtil,MultiThreadUtil
from machine import Timer

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

# WiFi配置
WIFI_SSID = 'AX6K'
WIFI_PASSWORD = '1234567890...'
#WIFI_SSID = '图图'
#WIFI_PASSWORD = 'nwl891126.ggl'

class MinBox():
    def __init__(self):
        self.c_ESP32160lcd = ESP32160lcd(ESP32160lcd_SDA_PIN,ESP32160lcd_SCL_PIN)
        self.c_Ds18b20TemperatureSensor = Ds18b20TemperatureSensor(Ds18b20TemperatureSensor_PIN)
        self.c_LightSensorThreePin = LightSensorThreePin(LightSensor_PIN)
        self.c_InfraredMotionSensor= InfraredMotionSensor(InfraredMotionSensor_PIN)
        self.c_InfraredMotionSensor.set_hander(self.infraredMotionSensor_hander)
        self.c_Relay = Relay(Relay_PIN)
        self.light_digital = 0
        self.temp = "1"
        self.wifi_is_connected_flag = False
        self.is_motion_detected = False
        self.current_datetime_hms = "00:00:00"

        self.timer = Timer(1)
        self.timer.init(period=1000 * 60 * 60 * 1, mode=Timer.PERIODIC, callback=self.sync_time_by_wifi)
        self.wifi_util = WiFiUtil()
        self.time_util = TimeUtil()
        self.multiThreadUtil = MultiThreadUtil()

    def do_work(self):
        #self.multiThreadUtil.start_new_thread(self.sync_time_by_wifi)
        self.sync_time_by_wifi()
        
        while(True):
            self.read_data_from_sensor()
            print("is_motion_detected: " + str(self.is_motion_detected) + " light_digital: " + str(self.light_digital) + " Temp: " + str(self.temp))
            self.show_datatime_temp_or_msg()


    def infraredMotionSensor_hander(self,*arges):
        if 0 == self.light_digital:
            print("hander ---> is_motion_detected: " + str(self.is_motion_detected) + " light_digital: " + str(self.light_digital) + " Temp: " + str(self.temp))
            return
        else:
            self.c_Relay.on()
            # 循环十五秒，打开继电器
            for i in range(15):
                self.show_datatime_temp_or_msg()
                if not self.c_InfraredMotionSensor.is_motion_detected():
                    break  # 如果在等待时间内没有人，则跳出循环

            # 当检测到没有人的时候，延迟5秒关闭
            for i in range(5): 
                self.show_datatime_temp_or_msg() 
            self.c_Relay.off()
            # self.c_ESP32160lcd.show_msg("Light: off","Temp: " + str(self.temp))
            return

    def show_datatime_temp_or_msg(self):
        self.c_ESP32160lcd.clear_msg()
        print("show_datatime_temp_or_msg ---> is_motion_detected: " + str(self.is_motion_detected) + " light_digital: " + str(self.light_digital) + " Temp: " + str(self.temp))
        self.read_data_from_sensor()
        if(self.wifi_is_connected_flag):
            self.c_ESP32160lcd.show_msg(self.time_util.get_current_datetime_hms(),"Temp: " + str(self.temp))
        else:
            self.c_ESP32160lcd.show_msg(str(self.is_motion_detected) + " --- " + str(self.light_digital) , ,"Temp: " + str(self.temp))
        time.sleep(1)
        self.c_ESP32160lcd.clear_msg()
    
    def read_data_from_sensor(self):
        self.device, self.temp = self.c_Ds18b20TemperatureSensor.collect_temperature_result()
        self.light_digital = self.c_LightSensorThreePin.read_light_digital()
        self.is_motion_detected = self.c_InfraredMotionSensor.is_motion_detected()

    def sync_time_by_wifi(self):       
        if (not self.wifi_is_connected_flag):
            self.wifi_util.do_connect(WIFI_SSID, WIFI_PASSWORD)
            if self.wifi_util.is_isconnected():
                self.wifi_is_connected_flag = True
                self.time_util.synchronised_local_time()
        else:
            self.time_util.synchronised_local_time()

    def wait_for_wifi_connection(wifi, timeout=15):
        start_time = utime.time()
        while not self.wifi_is_connected_flag() and (utime.time() - start_time) < timeout:
            utime.sleep(0.1)


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

