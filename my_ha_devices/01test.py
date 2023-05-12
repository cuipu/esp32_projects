'''
Author: cuipu g050505@gmail.com
Date: 2023-05-05 23:03:28
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-12 15:55:43
FilePath: \esp32_projects\my_ha_devices\01test.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import c_devices
from c_utils import MultiThreadUtil,WiFiUtil
import c_home_assistant_devices
import time
import _thread
import config
import machine
from umqttsimple import MQTTClient

# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT连接信息
MQTT_BROKER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'
MQTT_TOPIC = 'topic/relay'

# 继电器连接信息
RELAY_PIN = 22  # 请根据你的实际连接修改引脚号
RELAY_ON = 1  # 继电器打开状态（高电平）
RELAY_OFF = 0  # 继电器关闭状态（低电平）

# MQTT消息处理函数
def mqtt_callback(topic, msg):
    if msg == b'ON':
        relay.value(RELAY_ON)
        print('继电器打开')
    elif msg == b'OFF':
        relay.value(RELAY_OFF)
        print('继电器关闭')

def test_ha_mqtt():
    wifi = WiFiUtil()
    wifi.do_connect(WIFI_NAME, WIFI_PASSWORD)
    
    # 初始化继电器控制引脚
    relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
    relay.value(RELAY_OFF)  # 初始状态为关闭

    # 连接MQTT代理服务器
    mqtt_client = MQTTClient("esp32", MQTT_BROKER, port=MQTT_PORT,
                            user=MQTT_USER, password=MQTT_PASSWORD)
    mqtt_client.set_callback(mqtt_callback)
    mqtt_client.connect()
    mqtt_client.subscribe(MQTT_TOPIC)
    print('MQTT 连接成功')

    # 循环处理MQTT消息
    while True:
        mqtt_client.check_msg()

def config_test():
    wifi_ssid = config.wifi_config["ssid"]
    wifi_password = config.wifi_config["password"]

    print(wifi_ssid,wifi_password)

def home_assistant_device_test():

    #ha_temperature_sensor = c_home_assistant_devices.HATemperatureSensor()
    #ha_temperature_sensor.start_device()
    switch = c_home_assistant_devices.HASwitchDevice()
    switch.init()
    switch.start_device()
   

def ds18b20_temperature_sensor_test():
    while True:

        ds = Ds18b20TemperatureSensor(22)
        device, temp = ds.collect_temperature_result()
        print(device, temp)
        time.sleep(1)


def infrared_motion_sensor_test():
    infrared_motion_sensor = c_devices.InfraredMotionSensor(35)
    infrared_motion_sensor.set_hander(hander)


def light_sensor_test():
    light_sensor = c_devices.LightSensor(34, 21)
    # light_sensor.set_hander(hander)

    while True:
        analog_value = light_sensor.read_light_analog()
        digital_value = light_sensor.read_light_digital()
        print('analog_value : {} \n, digital_value : {} \n'.format(
            analog_value, digital_value))

        time.sleep(1)


def hander(*arges):

    relay = c_devices.Relay(22)
    light_sensor = c_devices.LightSensor(34, 21)
    # 判断亮度是否需要开灯
    light_analog_value = light_sensor.read_light_analog()
    print('light_analog_value: ', light_analog_value)
    if (light_analog_value>4000):
        # 开灯
        relay.on()
        print("open the light")
        time.sleep(10)
        relay.off()


def relay_test():
    relay = c_devices.Relay(22)
    relay.on()

    time.sleep(3)

    relay.off()


def esp32160lcd_test():
    es = c_home_assistant_devices.ESP32160lcd(22, 21)
    es.show_msg("first_row", "second_row")

# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT连接信息
MQTT_BROKER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'
MQTT_COMMAND_TOPIC = 'HA-esp32-relay/switch/set'
MQTT_STATE_TOPIC='HA-esp32-relay/switch/state'

# 继电器连接信息
RELAY_PIN = 22  # 请根据你的实际连接修改引脚号
RELAY_ON = 1  # 继电器打开状态（高电平）
RELAY_OFF = 0  # 继电器关闭状态（低电平）

class TestHaMqtt:
    def __init__(self):
        # 初始化继电器控制引脚
        #self.relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
        #self.relay.value(RELAY_OFF)  # 初始状态为关闭
        self.relay = c_devices.Relay(RELAY_PIN)

        wifi = WiFiUtil()
        wifi.do_connect(WIFI_NAME, WIFI_PASSWORD)

        # 连接MQTT代理服务器
        self.mqtt_client = MQTTClient("esp32-test", MQTT_BROKER, port=MQTT_PORT,
                                user=MQTT_USER, password=MQTT_PASSWORD)
        self.mqtt_client.set_callback(self.mqtt_callback)
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(MQTT_COMMAND_TOPIC)
        print('MQTT connected')


    # MQTT消息处理函数
    def mqtt_callback(self,topic, msg):
        print('topic: ' ,topic)
        if topic == MQTT_COMMAND_TOPIC.encode():
            if msg == b'ON':
                self.relay.on()
                self.mqtt_client.publish(MQTT_STATE_TOPIC, 'ON')
                print('relay is opened')
            elif msg == b'OFF':
                self.relay.off()
                self.mqtt_client.publish(MQTT_STATE_TOPIC, 'OFF')
                print('relay is closed')

    def test_ha_mqtt(self):
  
        # 循环处理MQTT消息
        while True:
            self.mqtt_client.check_msg()
            time.sleep(0.5)

def main():
    home_assistant_device_test()

    #test_ha = TestHaMqtt()

    #test_ha.test_ha_mqtt()


if __name__ == "__main__":
    main()
