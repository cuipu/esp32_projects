'''
Author: cuipu g050505@gmail.com
Date: 2023-05-11 22:03:16
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-06-21 00:26:03
FilePath: \esp32_projects\esp32_ha_devices\config.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
# Copyright 2020 LeMaRiva|tech lemariva.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

app_config = {
    'camera': 'M5CAMERA',  # camera -> 'ESP32-CAM' or 'M5CAMERA'
    "led": 14,  # led -> 4: ESP32-CAM or 14: M5CAMERA
}

wifi_config = {
    'ssid': 'TP-LINK_502_2.4G',
    'password': '1234567890...'
}
mqtt_config = {
    "server": "192.168.2.80",
    "port": 1883,
    "user": "test",
    "password": "1234560.",
    "keepalive": 0
}
