from c_home_assistant import HomeAssistantSensorDevice, HomeAssistantSwitchDevice
from c_devices import Ds18b20TemperatureSensor, PassiveBuzzer, Relay, ESP32160lcd, InfraredMotionSensor, LightSensor
from c_utils import MultiThreadUtil, TimeUtil
from umqttsimple import MQTTClient
import time
import sys
import uerrno
import gc
import micropython


HOMEASSISTANT_DEVICE_NAME = 'esp32-temperature'

HOMEASSISTANT_DEVICE_NAME_SENSOR = 'esp32-temperature'
# 名字不能太长
HOMEASSISTANT_SENSOR_NAME_TEMPERATURE = 'sensor'
HOMEASSISTANT_SENSOR_TYPE_TEMPERATURE = 'sensor'

OVER_WARINING_TEMPERATURE = 60

DS18B20_GPIO_NUM = 19
PASSIVE_BUZZER_GPIO_NUM = 23
TEMPERATURE_SEND_MSG_FREQ = 2

ESP32160LCD_SCL_GPIO_NUM = 22
ESP32160LCD_SDA_GPIO_NUM = 21

HOMEASSISTANT_DEVICE_NAME_SWITCH = 'esp32-relay'
# 名字不能太长
HOMEASSISTANT_SWITCH_NAME_RELAY_CONTROLLER = 'switch'
HOMEASSISTANT_SWITCH_TYPE_RELAY_CONTROLLER = 'relay'

MQTT_CLIENT_CHECK_MSG_FREQ = 0.1

# 单路继电器
RELAY_GPIO_NUM = 19
RELAY_STATUS_GPIO_NUM = 18

# 人体传感器
INFRARED_MOTION_SENSOR_GPIO_NUM = 35

# 光敏传感器
Light_Sensor_ANALOG_GPIO_NUM = 34
Light_Sensor_DIGITAL_GPIO_NUM = 21
LIGHT_SENSOR_THRESHOLD = 4000

RELAY_ON_TIME = 10

# MQTT_COMMAND_TOPIC = 'HA-esp32-relay/switch/set'
# MQTT_STATE_TOPIC='HA-esp32-relay/switch/state'

THRESHOLD_MEMORY = 1024


class HATemperatureSensor(HomeAssistantSensorDevice):
    def __init__(self):
        super().__init__()

        self.ds18b20_temperature_sensor = None
        self.passive_buzzer = None
        

        self.init()

    def init_device_info(self, homeassistant_device_name: str = None, homeassistant_device_sensor_name: str = None,
                         homeassistant_device_sensor_type: str = None):
        global MQTT_COMMAND_TOPIC
        # MQTT_COMMAND_TOPIC = self.command_topic

        self.homeassistant_device_name = HOMEASSISTANT_DEVICE_NAME_SENSOR
        self.homeassistant_sensor_name = HOMEASSISTANT_SENSOR_NAME_TEMPERATURE
        self.homeassistant_sensor_type = HOMEASSISTANT_SENSOR_TYPE_TEMPERATURE

        self.passive_buzzer = PassiveBuzzer(PASSIVE_BUZZER_GPIO_NUM)
        self.passive_buzzer.stop()

        self.esp32160lcd = ESP32160lcd(
            ESP32160LCD_SDA_GPIO_NUM, ESP32160LCD_SCL_GPIO_NUM)
        self.ds18b20_temperature_sensor = Ds18b20TemperatureSensor(
            DS18B20_GPIO_NUM)

    def do_mqtt_subscribe_topic_and_set_callback(self):
        pass
        # print('HATemperatureSensor command_topic : ', self.command_topic)

    def do_mqtt_publish_device_msg(self, device_msg: str):
        # 向mqtt推送数据的主题是state主题
        self.mqtt_client.publish(
            self.homeassistant_sensor_state_topic, device_msg)

    def sub_callback(self, topic, msg):
        pass
        # print(topic, msg)

    def do_work(self):
        while True:
            device, temperature = self.ds18b20_temperature_sensor.collect_temperature_result()
            self.do_mqtt_publish_device_msg(str(temperature))
            self.esp32160lcd.show_msg(self.time_util.get_current_datetime_hms(), "T:" + str(temperature))
            if temperature > OVER_WARINING_TEMPERATURE:
                self.passive_buzzer.play_mario()
            time.sleep(TEMPERATURE_SEND_MSG_FREQ)
            self.esp32160lcd.clear_msg()
            
        '''  
        try:
            while True:
                device, temperature = self.ds18b20_temperature_sensor.collect_temperature_result()
                self.do_mqtt_publish_device_msg(str(temperature))
                self.esp32160lcd.show_msg("temperature: ", str(temperature))
                if temperature > OVER_WARINING_TEMPERATURE:
                    self.passive_buzzer.play_mario()
                time.sleep(TEMPERATURE_SEND_MSG_FREQ)
                self.esp32160lcd.clear_msg()
        except MemoryError:
            print("Memory error occurred. Restarting...")
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            sys.exit()
        '''

    def multi_thread_start_device(self):
        self.multi_thread_util.start_new_thread(self.do_work)

    def start_device(self):
        self.do_work()


class HASwitchDevice(HomeAssistantSwitchDevice):
    def __init__(self):
        super().__init__()

        self.relay = None

        self.init()

    def init_device_info(self, homeassistant_device_name: str = None,
                         homeassistant_device_sensor_name: str = None, homeassistant_device_sensor_type: str = None):

        self.homeassistant_device_name = HOMEASSISTANT_DEVICE_NAME_SWITCH
        self.homeassistant_switch_name = HOMEASSISTANT_SWITCH_NAME_RELAY_CONTROLLER
        self.homeassistant_switch_type = HOMEASSISTANT_SWITCH_TYPE_RELAY_CONTROLLER

        self.relay_gpio_num = RELAY_GPIO_NUM

        self.relay = Relay(RELAY_GPIO_NUM,RELAY_STATUS_GPIO_NUM)

        # 人体传感器
        self.infrared_motion_sensor = InfraredMotionSensor(
            INFRARED_MOTION_SENSOR_GPIO_NUM)
        # 设置回调函数
        self.infrared_motion_sensor.set_hander(
            self.infrared_motion_sensor_hander)

        # 光敏传感器
        self.light_sensor = LightSensor(
            Light_Sensor_ANALOG_GPIO_NUM,
            Light_Sensor_DIGITAL_GPIO_NUM)

    def do_mqtt_subscribe_topic_and_set_callback(self):
        # 设置mqtt回调函数
        self.mqtt_client.set_callback(self.sub_callback)
        # 设置mqtt订阅的主题 HA-esp32-relay/switch/set
        self.mqtt_client.subscribe(self.command_topic)
        # self.mqtt_client.subscribe('HA-esp32-relay/switch/set')

    def sub_callback(self, topic, msg):
        if topic == self.command_topic.encode():
            # 发送继电器的状态传给HomeAssistant
            self.send_device_state_to_ha(msg)

    def do_mqtt_publish_device_msg(self, device_msg: str):
        # 向mqtt推送数据的主题是state主题
        self.mqtt_client.publish(
            self.homeassistant_switch_state_topic, device_msg)

    def send_device_state_to_ha(self, state):
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
                self.mqtt_client.check_msg()
                print("infrared_motion_sensor： " + str(self.infrared_motion_sensor.is_motion_detected())   + " light_sensor： " + str(self.light_sensor.read_light_analog()) 
                + " get_relay_state： " + str(self.relay.get_relay_status()))
                # 控制检测MQTT的频率
                time.sleep(MQTT_CLIENT_CHECK_MSG_FREQ)
        '''
        try:
            while True:
                self.mqtt_client.check_msg()
                # 控制检测MQTT的频率
                time.sleep(MQTT_CLIENT_CHECK_MSG_FREQ)
        except MemoryError:
            print("Memory error occurred. Restarting...")
        except OSError as e:
            error_code = e.args[0]
            error_name = uerrno.errorcode[error_code]
            print("OSError:", error_name)
        except KeyError as e:
            error_code = e.args[0]
            error_name = uerrno.errorcode[error_code]
            print("KeyError:", error_n)
        except Exception as e:
            print(f"Exception occurred: {e}")
            sys.print_exception(e)
        finally:
            time.sleep(10)
            # 重启设备
            machine.reset()
        '''
    # def multi_thread_start_device(self):
    #    self.multi_thread_util.start_new_thread(self.do_work)

    def start_device(self):
        self.do_work()

    def infrared_motion_sensor_hander(self, *arges):
        # 判断亮度是否需要开灯
        light_analog_value = self.light_sensor.read_light_analog()
        if ((light_analog_value > LIGHT_SENSOR_THRESHOLD) and self.relay.get_relay_status() == 0):
            # 开灯
            self.relay.on()
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "ON")
            time.sleep(5)
            self.relay.off()
            self.mqtt_client.publish(
                self.homeassistant_switch_state_topic, "OFF")
            # 设置成低电平，防止反复触发
            # self.infrared_motion_sensor.sensor_pin.value(0)

    def check_memory(self):
        free_mem = gc.mem_free()
        print("Free memory:", free_mem)
        if free_mem < THRESHOLD_MEMORY:
            micropython.mem_info()
            raise MemoryError("Low memory!")

def main():
    try:
        ha_temperature_sensor = HATemperatureSensor()
        ha_temperature_sensor.start_device()

        #ha_relay = HASwitchDevice()
        #ha_relay.start_device()
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
        print('system exit')
        sys.exit()


if __name__ == "__main__":
    main()