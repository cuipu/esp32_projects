'''
Author: cuipu g050505@gmail.com
Date: 2023-05-03 22:24:58
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-11 17:44:01
FilePath: \Demo\my_ha_devices\c_home_assistant.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import time
import ujson
from c_utils import FileUtil, WiFiUtils, MultiThreadUtil
from umqttsimple import MQTTClient
import config

# 内存不够，不从文件加载配置
ESP32_CONFIT = './esp32_config.txt'

# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT 服务器配置
MQTT_SERVER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'
MQTT_KEEPALIVE = 60

'''
class IHomeAssistant():

    def __init__(self):
        pass

    def init_config(self):
        pass

    def init_device_info(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
        pass

    def init_ha_device_config_content(self):
        pass

    def init_wifi(self):
        pass

    def init_mqtt(self):
        pass

    def do_mqtt_subscribe_topic_and_set_callback(self):
        pass
'''

class AbstractHomeAssistantDevice():
    def __init__(self):

        self.mqtt_server = None
        self.mqtt_port = None
        self.mqtt_user = None
        self.mqtt_password = None
        self.mqtt_keepalive = None
        
        self.mqtt_client = None

        self.wifi_name = None
        self.wifi_password = None
        self.wifi_utils = None

        self.multi_thread_util = MultiThreadUtil()

        
        self.init()

    def init(self):
        '''
        description: 初始化加载方法，定义了模板
        return {*}
        '''
        # self.load_config()
        self.init_device_info()
        self.init_wifi()
        self.init_mqtt()
        self.init_ha_device_config_content()
        self.register_device_to_ha()
        self.do_mqtt_subscribe_topic_and_set_callback()

    def load_config(self):
        '''
        description: 加载配置，因为内存太小，所以不从文件中加载配置，子类可以实现从别的数据源加载配置
        return {*}
        import config
        wifi_ssid = config.wifi_config["ssid"]
        wifi_password = config.wifi_config["password"]

        或者
        file_util = FileUtil()
        self.device_config_str = file_util.read_file_as_json(ESP32_CONFIT)
        # print(self.device_config_str)
        self.device_config_json = ujson.loads(self.device_config_str)
        print('device_config_json : \n', self.device_config_str)
        '''
        #wifi_ssid = config.wifi_config["ssid"]
        #wifi_password = config.wifi_config["password"]
        pass
    
    def init_device_info(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
        '''
        description: 初始化设备信息，可以传入，也可以从数据源配置中配置
        return {*}
        '''
        pass

        # 这里需要根据自己的情况进行适当修改配置，可以传入参入，也可以通过文件读取，子类自己实现
        # eg:
        # homeassistant_device_name = "ESP32-04"
        # homeassistant_device_sensor_name = "1"
        # homeassistant_device_sensor_type = "Temp"

    def init_ha_device_config_content(self):
        '''
        description: 初始化设备向HA发送的配置信息，例如sensor和switch，配置不同，发送的配置信息不同，子类自己实现
        return {*}
        '''
        pass

    def init_wifi(self):
        '''
        description: 初始化WiFi
        return {*}
        '''
        self.wifi_name = WIFI_NAME
        self.wifi_password = WIFI_PASSWORD

        self.wifi_utils = WiFiUtils()
        self.wifi_utils.do_connect(self.wifi_name, self.wifi_password)

    def init_mqtt(self):
        '''
        description: 初始化mqtt
        return {*}
        '''
        self.mqtt_server = MQTT_SERVER
        self.mqtt_port = MQTT_PORT
        self.mqtt_user = MQTT_USER
        self.mqtt_password = MQTT_PASSWORD
        self.mqtt_keepalive = MQTT_KEEPALIVE

  
        # 建立一个MQTT客户端
        self.mqtt_client = MQTTClient(self.homeassistant_device_name, self.mqtt_server,
                                      self.mqtt_port, self.mqtt_user, self.mqtt_password, self.mqtt_keepalive)
        # 建立连接
        self.mqtt_client.connect()

    def register_device_to_ha(self):
        '''
        description: 将设备和实体注册到HA
        return {*}
        '''
        pass
        # 告诉homeassistant服务器，有个新的设备实体要注册
        # sensor和switch订阅的主题不同，所以需要子类自己实现

    def do_mqtt_subscribe_topic_and_set_callback(self):
        '''
        description: # 订阅什么主题和设置什么回调函数由子类实现
        return {*}
        '''
        pass

    def do_mqtt_publish_device_msg(self, device_msg: str):
        '''
        description: 向mqtt推送数据的主题是state主题，推送的topic不同，由子类实现
        return {*}
        '''
        pass

    def sub_callback(self, topic, msg):
        '''
        description: 回调函数，收到服务器消息后会调用这个函数
        return {*}
        '''
        pass

    def start_device(self):
        '''
        description: 启动设备
        return {*}
        '''
        pass


'''
Author: cuipu g050505@gmail.com
Date: 2023-05-03 22:24:58
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-05 19:42:17
FilePath: \Demo\c_home_assistant.py
Description: HA传感器配置

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class HomeAssistantSensorDevice(AbstractHomeAssistantDevice):

    def __init__(self):

        self.homeassistant_device_name = None
        self.homeassistant_sensor_name = None
        self.homeassistant_sensor_type = None

        # HA接受设备数据的topic
        self.homeassistant_sensor_state_topic = None
        self.command_topic = None

    def init_ha_device_config_content(self):

        self.homeassistant_sensor_state_topic = "HA-%s/%s/state" % (
            self.homeassistant_device_name, self.homeassistant_sensor_name)
        # 本ESP32订阅的控制的主题，sensor一般不用，因为sensor只是向HA发送数据，不需要控制
        self.command_topic = "HA-%s/%s/set" % (
            self.homeassistant_device_name, self.homeassistant_sensor_name)

        # 下面的内容是固定格式，只需要替换对应数据就行，传感器用sensor，控制器用switch
        self.homeassistant_sensor_config_topic = "homeassistant/sensor/HA/HA-%s-%s/config" % (
            self.homeassistant_device_name, self.homeassistant_sensor_name)

        self.homeassistant_config_content = {
            "unique_id": "HA-%s-%s" % (self.homeassistant_device_name, self.homeassistant_sensor_name),
            "name": self.homeassistant_sensor_type,
            "icon": "mdi:thermometer",
            "state_topic": self.homeassistant_sensor_state_topic,
            "json_attributes_topic": "HA-%s/%s/attributes" % (self.homeassistant_device_name, self.homeassistant_sensor_name),
            # "unit_of_measurement": "℃",  # 注意这个数据在ESP32中会导致发送失败，即℃符号导致发送失败，所以不要发这种数据
            # "command_topic": self.command_topic,
            "device": {
                "identifiers": self.homeassistant_device_name,
                "manufacturer": "Mr.Cui",
                "model": "HA",
                "name": self.homeassistant_device_name,
                "sw_version": "1.0"
            }
        }

        self.send_content = ujson.dumps(self.homeassistant_config_content)
        # 告诉homeassistant服务器，有个新的设备实体要注册
        #self.mqtt_client.publish(
        #    self.homeassistant_sensor_config_topic, self.send_content)
        
    def register_device_to_ha(self):
            # 告诉homeassistant服务器，有个新的设备实体要注册
            self.mqtt_client.publish(
                self.homeassistant_sensor_config_topic, self.send_content)


'''
Author: cuipu g050505@gmail.com
Date: 2023-05-03 22:24:58
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-05 19:42:17
FilePath: \Demo\c_home_assistant.py
Description: HA控制器设备配置

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 

详细配置参考：
https://www.home-assistant.io/integrations/mqtt/


When using Home Assistant’s YAML editor for formatting JSON you should take special care if payload contains template content. 
Home Assistant will force you in to the YAML editor and will treat your definition as a template. 
Make sure you escape the template blocks as like in the example below. 
Home Assistant will convert the result to a string and will pass it to the MQTT publish service.

service: mqtt.publish
data:
  topic: homeassistant/sensor/Acurite-986-1R-51778/config
  payload: >-
    {"device_class": "temperature",
    "name": "Acurite-986-1R-51778-T",
    "unit_of_measurement": "\u00b0C",
    "value_template": "{% raw %}{{ value|float }}{% endraw %}",
    "state_topic": "rtl_433/rtl433/devices/Acurite-986/1R/51778/temperature_C",
    "unique_id": "Acurite-986-1R-51778-T",
    "device": {
    "identifiers": "Acurite-986-1R-51778",
    "name": "Acurite-986-1R-51778",
    "model": "Acurite-986",
    "manufacturer": "rtl_433" }
    }

Example of how to use qos and retain:

topic: home-assistant/light/1/command
payload: on
qos: 2
retain: true

'''


class HomeAssistantSwitchDevice(AbstractHomeAssistantDevice):

    def __init__(self):
        self.homeassistant_device_name = None
        self.homeassistant_switch_name = None
        self.homeassistant_switch_type = None 

        # HA接受设备数据的topic
        self.homeassistant_switch_state_topic = None

        # HA向设备发送数据的topic
        self.command_topic = None

    def init_ha_device_config_content(self):

        # self.mqtt_client.connect()

        self.homeassistant_switch_state_topic = "HA-%s/%s/state" % (
            self.homeassistant_device_name, self.homeassistant_switch_name)
        # 订阅HA控制设备的主题
        self.command_topic = "HA-%s/%s/set" % (
            self.homeassistant_device_name, self.homeassistant_switch_name)

        # 下面的内容是固定格式，只需要替换对应数据就行，传感器用sensor，控制器用switch
        self.homeassistant_switch_config_topic = "homeassistant/switch/HA/HA-%s-%s/config" % (
            self.homeassistant_device_name, self.homeassistant_switch_name)

        self.homeassistant_config_content = {
            "unique_id": "HA-%s-%s" % (self.homeassistant_device_name, self.homeassistant_switch_name),
            "name": self.homeassistant_switch_type,
            "icon": "mdi:thermometer",
            "state_topic": self.homeassistant_switch_state_topic,
            "json_attributes_topic": "HA-%s/%s/attributes" % (self.homeassistant_device_name, self.homeassistant_switch_name),
            # "unit_of_measurement": "℃",  # 注意这个数据在ESP32中会导致发送失败，即℃符号导致发送失败，所以不要发这种数据
            "command_topic": self.command_topic,
            "device": {
                "identifiers": self.homeassistant_device_name,
                "manufacturer": "Mr.Cui",
                "model": "HA",
                "name": self.homeassistant_device_name,
                "sw_version": "1.0"
            }
        }

        self.send_content = ujson.dumps(self.homeassistant_config_content)

        print('>>>{}<<<\n>>>{}<<<\n'.format(self.command_topic, 
        self.homeassistant_switch_state_topic))

    def register_device_to_ha(self):
            # 告诉homeassistant服务器，有个新的设备实体要注册
            self.mqtt_client.publish(
                self.homeassistant_switch_config_topic, self.send_content)
