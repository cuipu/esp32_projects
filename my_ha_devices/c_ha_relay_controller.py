from c_devices import Relay, ESP32160lcd, InfraredMotionSensor, LightSensor
from c_utils import MultiThreadUtil,  WiFiUtils
from umqttsimple import MQTTClient
import config
import ujson
import time
import sys


# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT 服务器配置
MQTT_SERVER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'
MQTT_KEEPALIVE = 60


HOMEASSISTANT_DEVICE_NAME_SWITCH = 'esp32-relay'
# 名字不能太长
HOMEASSISTANT_SWITCH_NAME_RELAY_CONTROLLER = 'switch'
HOMEASSISTANT_SWITCH_TYPE_RELAY_CONTROLLER = 'relay'

MQTT_CLIENT_CHECK_MSG_FREQ = 0.5

RELAY_GPIO_NUM = 22
# 人体传感器
INFRARED_MOTION_SENSOR_GPIO_NUM = 35

# 光敏传感器
Light_Sensor_ANALOG_GPIO_NUM = 34
Light_Sensor_DIGITAL_GPIO_NUM = 21
LIGHT_SENSOR_THRESHOLD = 4000

class HARelayController():
    def __init__(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
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

        # HA接受设备数据的topic
        self.homeassistant_device_name = None
        self.homeassistant_switch_name = None
        self.homeassistant_switch_type = None 

        # HA接受设备数据的topic
        self.homeassistant_switch_state_topic = None

        # HA向设备发送数据的topic
        self.command_topic = None

        self.relay = None

        self.init()

    def init(self):
        self.init_device_info()
        self.init_wifi()
        self.init_mqtt()
        self.init_ha_device_config_content()
        self.register_device_to_ha()
        self.do_mqtt_subscribe_topic_and_set_callback()


    def init_wifi(self):
        self.wifi_name = WIFI_NAME
        self.wifi_password = WIFI_PASSWORD

        self.wifi_utils = WiFiUtils()
        self.wifi_utils.do_connect(self.wifi_name, self.wifi_password)

    def init_mqtt(self):

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

    def init_device_info(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
        self.homeassistant_device_name = HOMEASSISTANT_DEVICE_NAME_SWITCH
        self.homeassistant_switch_name = HOMEASSISTANT_SWITCH_NAME_RELAY_CONTROLLER
        self.homeassistant_switch_type = HOMEASSISTANT_SWITCH_TYPE_RELAY_CONTROLLER

        self.relay_gpio_num = RELAY_GPIO_NUM

        self.relay = Relay(RELAY_GPIO_NUM)

        # 人体传感器
        self.infrared_motion_sensor = InfraredMotionSensor(INFRARED_MOTION_SENSOR_GPIO_NUM)
        # 设置回调函数
        self.infrared_motion_sensor.set_hander(self.infrared_motion_sensor_hander)

        # 光敏传感器
        self.light_sensor = LightSensor(Light_Sensor_ANALOG_GPIO_NUM,Light_Sensor_DIGITAL_GPIO_NUM)

    def register_device_to_ha(self):
        # 告诉homeassistant服务器，有个新的设备实体要注册
        self.mqtt_client.publish(
            self.homeassistant_switch_config_topic, self.send_content)


    def do_mqtt_subscribe_topic_and_set_callback(self):
                    
        # 设置mqtt回调函数
        self.mqtt_client.set_callback(self.sub_callback)
        # 设置mqtt订阅的主题
        self.mqtt_client.subscribe(self.command_topic)
        

    def sub_callback(self, topic, msg):
        if topic == self.command_topic.encode():
            # 发送继电器的状态传给HomeAssistant
            self.send_relay_state_to_ha(msg)

    def do_mqtt_publish_device_msg(self, device_msg: str):
        # 向mqtt推送数据的主题是state主题
        self.mqtt_client.publish(
            self.homeassistant_switch_state_topic, device_msg)

    def send_relay_state_to_ha(self, state):
        # 发送继电器状态给HomeAssistant
        if state == b"ON":
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "ON")
            self.relay.on()
        else:
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "OFF")
            self.relay.off()

    def do_work(self):
        while True:
            try:
                # self.mqtt_client.check_msg()
                self.mqtt_client.check_msg()
                # 控制检测MQTT的频率
                time.sleep(MQTT_CLIENT_CHECK_MSG_FREQ)
            except Exception as e:
                print("Exception: {}".format(e))

    def multi_thread_start_device(self):
        self.multi_thread_util.start_new_thread(self.do_work())

    def start_device(self):
        self.do_work()

    def infrared_motion_sensor_hander(self,*arges):
        # 判断亮度是否需要开灯
        light_analog_value = self.light_sensor.read_light_analog()
        if (light_analog_value>LIGHT_SENSOR_THRESHOLD):
            # 开灯
            self.relay.on()
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "ON")
            time.sleep(10)
            self.relay.off()
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "OFF")
            # 设置成低电平，防止反复触发
            self.infrared_motion_sensor.sensor_pin.value(0)


def ha_relay_test():
    ha_relay = HARelayController()
    '''
    ha_relay.init_device_info()
    ha_relay.init_wifi()
    ha_relay.init_mqtt()
    ha_relay.init_ha_device_config_content()
    ha_relay.register_device_to_ha()
    ha_relay.do_mqtt_subscribe_topic_and_set_callback()
    '''
    ha_relay.start_device()

def main():
    ha_relay_test()
    # esp32160lcd_test()
    # ds18b20_temperature_sensor_test()


if __name__ == "__main__":
    main()
