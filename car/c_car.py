from c_utils import WiFiUtil
from c_devices import Relay
from umqttsimple import MQTTClient
from machine import Pin
import time
import sys

'''

左前轮：Left front wheel
右前轮：Right front wheel
左后轮：Left rear wheel
右后轮：Right rear wheel
'''

# 左前轮电机
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1 = 27
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2 = 14

# 右前轮电机
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1 = 26
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2 = 25

# 左后轮电机
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1 = 17
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2 = 5

# 右后轮电机
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1 = 16
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2 = 4

class Car:
    def __init__(self):
        self.left_front_wheel_motor_a1_pin1 = Pin(LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.left_front_wheel_motor_a1_pin2 = Pin(LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.right_front_wheel_motor_b1_pin1 = Pin(RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.right_front_wheel_motor_b1_pin2 = Pin(RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.left_rear_wheel_motor_b2_pin1 = Pin(LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.left_rear_wheel_motor_b2_pin2 = Pin(LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.right_rear_wheel_motor_a2_pin1 = Pin(RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.right_rear_wheel_motor_a2_pin2 = Pin(RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.relay = None

        self.init_device()
    def init_device(self):
        self.relay = Relay(RELAY_GPIO_NUM)
        self.relay.off()

    def move_forward(self):
        self.left_front_wheel_motor_a1_pin1.value(1)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(1) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(1) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(1) 
        self.right_rear_wheel_motor_a2_pin2.value(0)

    def move_backward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(1)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(1) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(1) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(1)
        
    def move_leftward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(1)

        self.right_front_wheel_motor_b1_pin1.value(1) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(1) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(1) 

    def move_rightward(self):
        self.left_front_wheel_motor_a1_pin1.value(1)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(1) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(1) 

        self.right_rear_wheel_motor_a2_pin1.value(1)
        self.right_rear_wheel_motor_a2_pin2.value(0) 
    
    def left_forward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(1) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(1) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(0) 

    def right_forward(self):
        self.left_front_wheel_motor_a1_pin1.value(1)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(1)
        self.right_rear_wheel_motor_a2_pin2.value(0)

    def left_backward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(1)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(1)

    def right_backward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(1) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(1) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(0) 

    def rotate_leftward(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(1)

        self.right_front_wheel_motor_b1_pin1.value(1) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(1) 

        self.right_rear_wheel_motor_a2_pin1.value(1)
        self.right_rear_wheel_motor_a2_pin2.value(0) 

    def rotate_rightward(self):
        self.left_front_wheel_motor_a1_pin1.value(1)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(1) 

        self.left_rear_wheel_motor_b2_pin1.value(1) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(1) 


    def stop(self):
        self.left_front_wheel_motor_a1_pin1.value(0)
        self.left_front_wheel_motor_a1_pin2.value(0)

        self.right_front_wheel_motor_b1_pin1.value(0) 
        self.right_front_wheel_motor_b1_pin2.value(0) 

        self.left_rear_wheel_motor_b2_pin1.value(0) 
        self.left_rear_wheel_motor_b2_pin2.value(0) 

        self.right_rear_wheel_motor_a2_pin1.value(0)
        self.right_rear_wheel_motor_a2_pin2.value(0) 
    

# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT 服务器配置
MQTTT_CLIENT_ID = 'esp32-car'
MQTT_SERVER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'

MQTT_COMMAND_TOPIC_CONTROL_CAR = 'control car'
MQTT_CLIENT_CHECK_MSG_FREQ = 0.1

RELAY_GPIO_NUM = 33

TRIG_GPIO_NUM = 1
ECHO_GPIO_NUM = 1

# 刹车距离，单位 cm
BRAKING_DISTANCE = 10
class CarController():
    def __init__(self):
        self.mqtt_client = None
        self.car = Car()
        #self.ultrasonic_distance_sensor = UltrasonicDistanceSensor(TRIG_GPIO_NUM,ECHO_GPIO_NUM)
        self.wifi_util = None
        self.relay = None

        self.init_wifi()
        self.init_mqtt()
        self.init_device()

    def init_wifi(self):
        self.wifi_util = WiFiUtil()
        self.wifi_util.do_connect(WIFI_NAME,WIFI_PASSWORD)

    def init_mqtt(self):
        # 连接MQTT代理服务器
        self.mqtt_client = MQTTClient(MQTTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT,
                                user=MQTT_USER, password=MQTT_PASSWORD)
        self.mqtt_client.set_callback(self.mqtt_callback)
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(MQTT_COMMAND_TOPIC_CONTROL_CAR)
        print('MQTT connected')

    def init_device(self):
        self.relay = Relay(RELAY_GPIO_NUM)
        self.relay.off()

     # MQTT消息处理函数
    def mqtt_callback(self,topic, msg):
        '''
        定义：参考键盘小键盘
        8：向前
        2：向后
        4：向左
        6：向右
        7：向左上
        9：向右上
        1：向左下
        3：向右下

        44：左旋转
        66：右旋转

        0：停止

        '''
        print('topic: ' ,topic)
        if topic == MQTT_COMMAND_TOPIC_CONTROL_CAR.encode():
            if b'8'== msg:
                self.car.move_forward()
            elif b'2'== msg:
                self.car.move_backward()
            elif b'4' == msg:
                self.car.move_leftward()
            elif b'6'== msg:
                self.car.move_rightward()
            elif b'7'== msg:
                self.car.left_forward()
            elif b'9'== msg:
                self.car.right_forward()
            elif b'1'== msg:
                self.car.left_backward()
            elif b'3'== msg:
                self.car.right_backward()
            elif b'44'== msg:
                self.car.rotate_leftward()
            elif b'66' == msg:
                self.car.rotate_rightward()
            elif b'0' == msg:
                self.car.stop()
            elif b'on' == msg:
                self.relay.on()
            elif b'off' == msg:
                self.relay.off()
            else:
                self.car.stop()


    def do_distance_monitoring(self):
        '''
        description: 监测距离，如果太近则停止
        return {*}
        '''                
        pass

    def do_work(self):
        try:
            while True:
                #if self.ultrasonic_distance_sensor.do_measure() < BRAKING_DISTANCE:
                #    self.car.stop()
                #else:
                self.mqtt_client.check_msg()
                time.sleep(MQTT_CLIENT_CHECK_MSG_FREQ)
        except MemoryError:
            print("Memory error occurred. Restarting...")
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            sys.exit()


def car_test():
   
    car = Car()
    car.relay.on()

    car.left_front_wheel_motor_a1_pin1.value(0)
    car.left_front_wheel_motor_a1_pin2.value(0)

    car.right_front_wheel_motor_b1_pin1.value(0) 
    car.right_front_wheel_motor_b1_pin2.value(0) 

    car.left_rear_wheel_motor_b2_pin1.value(0) 
    car.left_rear_wheel_motor_b2_pin2.value(0) 

    car.right_rear_wheel_motor_a2_pin1.value(0)
    car.right_rear_wheel_motor_a2_pin2.value(0)

    time.sleep(3)
    car.stop()

    '''
    car_controller = CarController()
    car_controller.do_work()
    '''
def main():
    car_test()


if __name__ == "__main__":
    main()


