'''
Author: cuipu g050505@gmail.com
Date: 2023-05-10 17:33:58
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-10 20:00:03
FilePath: \Demo\my_ha_devices\03test_ha_mqtt.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import c_devices
from c_utils import MultiThreadUtil,WiFiUtils
import c_home_assistant_devices
import time
import _thread
import config
import machine
from umqttsimple import MQTTClient
#import ulogging as logging
#logging.basicConfig(level=logging.INFO)
#log = logging.getLogger('app')

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

        wifi = WiFiUtils()
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
            elif msg == b'OFF':
                self.relay.off()
                self.mqtt_client.publish(MQTT_STATE_TOPIC, 'OFF')
                print('继电器关闭')

    def test_ha_mqtt(self):
  
        # 循环处理MQTT消息
        while True:
            self.mqtt_client.check_msg()
            time.sleep(0.5)


def main():
    test_ha = TestHaMqtt()

    test_ha.test_ha_mqtt()
    # esp32160lcd_test()
    # ds18b20_temperature_sensor_test()


if __name__ == "__main__":
    main()
