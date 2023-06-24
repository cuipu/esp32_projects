'''
Author: cuipu g050505@gmail.com
Date: 2023-06-21 00:41:43
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-06-22 18:50:56
FilePath: \esp32_projects\esp32_ha_devices\temperature_sensor_config.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
wifi_confi = {
    "ssid": "AX6K",
    "password": "1234567890..."
},

mqtt_config = {
    "server": "192.168.2.80",
    "port": 1883,
    "user": "test",
    "password": "1234560.",
    "keepalive": 0
}

homeassistant_config = {
    "device_name" :  "esp32-tepmerature",
}