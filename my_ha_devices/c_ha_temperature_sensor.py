from c_home_assistant import HomeAssistantSensorDevice, HomeAssistantCommandDevice
from c_devices import Ds18b20TemperatureSensor, PassiveBuzzer, Relay
from c_utils import MultiThreadUtil, FileUtil, WiFiUtils
import time
import sys

ESP32_CONFIT = './esp32_config.txt'

WIFI_NAME = 'wifi_name'
WIFI_PASSWORD = 'wifi_password'

# MQTT 服务器配置
MQTT_SERVER = 'mqtt_server'
MQTT_PORT = 'mqtt_port'
MQTT_USER = 'mqtt_user'
MQTT_PASSWORD = 'mqtt_password'
MQTT_KEEPALIVE = 'mqtt_keepalive'


HOMEASSISTANT_DEVICE_NAME = 'homeassistant_device_name'
HOMEASSISTANT_SENSOR_NAME_TEMPERATURE = 'homeassistant_sensor_name_temperature'
HOMEASSISTANT_SENSOR_TYPE_TEMPERATURE = 'homeassistant_sensor_type_temperature'

DS18B20_GPIO_NUM = 'ds18b20_gpio_num'
PASSIVE_BUZZER_GPIO_NUM = 'passive_buzzer_gpio_num'
TEMPERATURE_SEND_MSG_FREQ = 'temperature_send_msg_freq'

HOMEASSISTANT_SENSOR_NAME_RELAY_CONTROLLER = 'homeassistant_sensor_name_relay_controller'
HOMEASSISTANT_SENSOR_TYPE_RELAY_CONTROLLER = 'homeassistant_sensor_type_relay_controller'
RELAY_GPIO_NUM = 'relay_gpio_num'


class HATemperatureSensor():

    def __init__(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
        self.homeassistant_device_name = None
        self.homeassistant_device_sensor_name = None
        self.homeassistant_device_sensor_type = None

        self.homeassistant_config_topic = None
        self.homeassistant_config_content = None
        self.send_content = None

        # HA接受设备数据的topic
        self.homeassistant_state_topic = None

        # HA向设备发送数据的topic
        self.command_topic = None

        self.mqtt_client = None
        self.mqtt_server = None
        self.mqtt_port = None
        self.mqtt_user = None
        self.mqtt_password = None
        self.mqtt_keepalive = None

        self.wifi_name = None
        self.wifi_password = None

        self.device_config_str = None
        self.device_config_json = None

        self.init()

    def read_config_from_file(self):
        file_util = FileUtil()
        self.device_config_str = file_util.read_file_as_json(ESP32_CONFIT)
        # print(self.device_config_str)
        self.device_config_json = ujson.loads(self.device_config_str)
        print('device_config_json : \n', self.device_config_str)

    def init_wifi(self):
        self.wifi_name = self.device_config_json.get(WIFI_NAME)
        self.wifi_password = self.device_config_json.get(WIFI_PASSWORD)

        wifi_utils = WiFiUtils()
        wifi_utils.do_connect(self.wifi_name, self.wifi_password)

    def init_mqtt(self):

        self.mqtt_server = self.device_config_json.get(MQTT_SERVER)
        self.mqtt_port = int(self.device_config_json.get(MQTT_PORT))
        self.mqtt_user = self.device_config_json.get(MQTT_USER)
        self.mqtt_password = self.device_config_json.get(MQTT_PASSWORD)
        self.mqtt_keepalive = int(
            self.device_config_json.get(MQTT_KEEPALIVE))
        print('mqtt info : \n', self.homeassistant_device_name, self.mqtt_server,
              self.mqtt_port, self.mqtt_user, self.mqtt_password, self.mqtt_keepalive)
        # 建立一个MQTT客户端
        self.mqtt_client = MQTTClient(self.homeassistant_device_name, self.mqtt_server,
                                      self.mqtt_port, self.mqtt_user, self.mqtt_password, self.mqtt_keepalive)
        # 建立连接
        self.mqtt_client.connect()

    def register_device_to_ha(self):
        # 告诉homeassistant服务器，有个新的设备实体要注册
        self.mqtt_client.publish(
            self.homeassistant_config_topic, self.send_content)

    def init_ha_device_config_content(self):
        # self.mqtt_client.connect()

        # 本ESP32订阅的控制的主题，sensor一般不用，因为sensor只是向HA发送数据，不需要控制
        self.command_topic = "HA-%s/%s/set" % (
            self.homeassistant_device_name, self.homeassistant_device_sensor_name)

        # 下面的内容是固定格式，只需要替换对应数据就行，传感器用sensor，控制器用switch
        self.homeassistant_config_topic = "homeassistant/sensor/HA/HA-%s-%s/config" % (
            self.homeassistant_device_name, self.homeassistant_device_sensor_name)

        self.homeassistant_config_content = {
            "unique_id": "HA-%s-%s" % (self.homeassistant_device_name, self.homeassistant_device_sensor_name),
            "name": self.homeassistant_device_sensor_type,
            "icon": "mdi:thermometer",
            "state_topic": "HA-%s/%s/state" % (self.homeassistant_device_name, self.homeassistant_device_sensor_name),
            "json_attributes_topic": "HA-%s/%s/attributes" % (self.homeassistant_device_name, self.homeassistant_device_sensor_name),
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

        self.homeassistant_state_topic = "HA-%s/%s/state" % (
            self.homeassistant_device_name, self.homeassistant_device_sensor_name)

        self.send_content = ujson.dumps(self.homeassistant_config_content)

    def init_ha_device_info(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):
        self.homeassistant_device_name = self.device_config_json.get(
            HOMEASSISTANT_DEVICE_NAME)
        self.homeassistant_device_sensor_name = self.device_config_json.get(
            HOMEASSISTANT_SENSOR_NAME_TEMPERATURE)
        self.homeassistant_device_sensor_type = self.device_config_json.get(
            HOMEASSISTANT_SENSOR_TYPE_TEMPERATURE)

        ds18b20_temperature_sensor_gpio_num = self.device_config_json.get(
            DS18B20_GPIO_NUM)
        self.ds18b20_temperature_sensor = Ds18b20TemperatureSensor(
            int(ds18b20_temperature_sensor_gpio_num))
        passive_buzzer_gpio_num = self.device_config_json.get(
            PASSIVE_BUZZER_GPIO_NUM)

        self.passive_buzzer = PassiveBuzzer(int(passive_buzzer_gpio_num))

        self.temperature_send_msg_freq = float(
            self.device_config_json.get(TEMPERATURE_SEND_MSG_FREQ))

    def do_mqtt_subscribe_topic_and_set_callback(self):
        print('HATemperatureSensor command_topic : ', self.command_topic)
        # 设置mqtt回调函数
        self.mqtt_client.set_callback(self.sub_callback)
        # 设置mqtt订阅的主题 sensor
        self.mqtt_client.subscribe(self.command_topic)

    def do_mqtt_publish_device_msg(self, device_msg: str):
        print('HATemperatureSensor homeassistant_state_topic : ',
              self.homeassistant_state_topic)
        # 向mqtt推送数据的主题是state主题

        self.mqtt_client.publish(self.homeassistant_state_topic, device_msg)

    def sub_callback(self, topic, msg):
        print(topic, msg)

    def start_device(self):
        while True:
            device, temperature = self.ds18b20_temperature_sensor.collect_temperature_result()
            print('{} temperature: {} ℃'.format(device, temperature))

            self.mqtt_client.publish(
                self.homeassistant_state_topic, str(temperature))
            # TODO 这里有问题，不知道怎么回事，
            # self.do_mqtt_publish_device_msg(str(temperature))
            if temperature > 60:
                self.passive_buzzer.play_mario()
            time.sleep(self.temperature_send_msg_freq)
    