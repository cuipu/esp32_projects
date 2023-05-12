from machine import Pin
from c_devices import UltrasonicDistanceSensor
from umqttsimple import MQTTClient
import time
import sys

'''

左前轮：Left front wheel
右前轮：Right front wheel
左后轮：Left rear wheel
右后轮：Right rear wheel
前进：Forward
后退：Backward
左转：Left turn
右转：Right turn
'''

# 左前轮电机
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1= 1
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2=1

# 右前轮电机
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1=1
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2=1

# 左后轮电机
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1=1
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2=1

# 右后轮电机
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1=1
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2=1

class Car:
    def __init__(self):
        self.left_front_wheel_motor_pin1 = Pin(LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.left_front_wheel_motor_pin2 = Pin(LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.right_front_wheel_motor_pin1 = Pin(RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.right_front_wheel_motor_pin2 = Pin(RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.left_rear_wheel_motor_pin1 = Pin(LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.left_rear_wheel_motor_pin2 = Pin(LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

        self.right_rear_wheel_motor_pin1 = Pin(RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1, Pin.OUT)
        self.right_rear_wheel_motor_pin2 = Pin(RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2, Pin.OUT)

    def turn_left(self):
        self.left_front_wheel_motor_pin1.value(1)
        self.left_front_wheel_motor_pin2.value(0)

        self.right_front_wheel_motor_pin1.value(0) 
        self.right_front_wheel_motor_pin2.value(1) 

        self.left_rear_wheel_motor_pin1.value(0) 
        self.left_rear_wheel_motor_pin2.value(1) 

        self.right_rear_wheel_motor_pin1.value(1)
        self.right_rear_wheel_motor_pin2.value(0) 

    def turn_right(self):
        self.left_front_wheel_motor_pin1.value(0)
        self.left_front_wheel_motor_pin2.value(1)

        self.right_front_wheel_motor_pin1.value(1) 
        self.right_front_wheel_motor_pin2.value(0) 

        self.left_rear_wheel_motor_pin1.value(1) 
        self.left_rear_wheel_motor_pin2.value(0) 

        self.right_rear_wheel_motor_pin1.value(0)
        self.right_rear_wheel_motor_pin2.value(1) 

    def move_forward(self):
        self.left_front_wheel_motor_pin1.value(0)
        self.left_front_wheel_motor_pin2.value(0)

        self.right_front_wheel_motor_pin1.value(0) 
        self.right_front_wheel_motor_pin2.value(0) 

        self.left_rear_wheel_motor_pin1.value(0) 
        self.left_rear_wheel_motor_pin2.value(0) 

        self.right_rear_wheel_motor_pin1.value(0)
        self.right_rear_wheel_motor_pin2.value(0) 

    def move_backward(self):
        self.left_front_wheel_motor_pin1.value(1)
        self.left_front_wheel_motor_pin2.value(0)

        self.right_front_wheel_motor_pin1.value(1) 
        self.right_front_wheel_motor_pin2.value(0) 

        self.left_rear_wheel_motor_pin1.value(1) 
        self.left_rear_wheel_motor_pin2.value(0) 

        self.right_rear_wheel_motor_pin1.value(1)
        self.right_rear_wheel_motor_pin2.value(0) 

    def stop(self):
        self.left_front_wheel_motor_pin1.value(0)
        self.left_front_wheel_motor_pin2.value(0)

        self.right_front_wheel_motor_pin1.value(0) 
        self.right_front_wheel_motor_pin2.value(0) 

        self.left_rear_wheel_motor_pin1.value(0) 
        self.left_rear_wheel_motor_pin2.value(0) 

        self.right_rear_wheel_motor_pin1.value(0)
        self.right_rear_wheel_motor_pin2.value(0) 



# MQTT 服务器配置
MQTTT_CLIENT_ID = 'esp32-car'
MQTT_SERVER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'

MQTT_COMMAND_TOPIC_CONTROL_CAR = 'control car'
MQTT_CLIENT_CHECK_MSG_FREQ = 0.1

TRIG_GPIO_NUM = 1
ECHO_GPIO_NUM = 1

# 刹车距离，单位 cm
BRAKING_DISTANCE = 10
class CarController():
    def __init__(self):
        self.mqtt_client = None
        self.car = Car()
        self.ultrasonic_distance_sensor = UltrasonicDistanceSensor(TRIG_GPIO_NUM,ECHO_GPIO_NUM)

    def init_mqtt(self):
        # 连接MQTT代理服务器
        self.mqtt_client = MQTTClient(MQTTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT,
                                user=MQTT_USER, password=MQTT_PASSWORD)
        self.mqtt_client.set_callback(self.mqtt_callback)
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(MQTT_COMMAND_TOPIC_CONTROL_CAR)
        print('MQTT connected')

     # MQTT消息处理函数
    def mqtt_callback(self,topic, msg):
        print('topic: ' ,topic)
        if topic == MQTT_COMMAND_TOPIC_CONTROL_CAR.encode():
            if 'f' == msg:
                self.car.move_forward()
            elif 'b'== msg:
                self.car.move_backward()
            elif 'l' == msg:
                self.car.turn_left()
            elif 'r' == msg:
                self.car.turn_right()
            elif 's' == msg:
                self.car.stop()
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
                if self.ultrasonic_distance_sensor.do_measure() < BRAKING_DISTANCE:
                    self.car.stop()
                else:
                    self.mqtt_client.check_msg()
                time.sleep(MQTT_CLIENT_CHECK_MSG_FREQ)
        except MemoryError:
            print("Memory error occurred. Restarting...")
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            sys.exit()