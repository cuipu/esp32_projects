from c_utils import WiFiUtil,MultiThreadUtil
from c_devices import Relay,UltrasonicDistanceSensor
from umqttsimple import MQTTClient
from machine import Pin
import time
import sys
import _thread


class MotorController:
    def __init__(self, in1_gpio_num, in2_gpio_num, ena_pin_gpio_num = None, pwm_gpio_num=None):
        
        self.in1_pin = Pin(in1_gpio_num, Pin.OUT)
        self.in2_pin = Pin(in2_gpio_num, Pin.OUT)
        self.ena_pin = Pin(ena_pin_gpio_num, Pin.OUT) if ena_pin_gpio_num is not None else None
        self.pwm_pin = PWM(pwm_gpio_num) if pwm_gpio_num is not None else None


    def set_speed(self, speed = 50):
        if self.pwm_pin is not None:
            self.pwm_pin.duty(speed)

    def forward(self, speed = 50):
        self.set_speed(speed)
        if self.ena_pin is not None:
            self.ena_pin.value(1)
        self.in1_pin.value(1)
        self.in2_pin.value(0)

    def backward(self, speed = 50):
        self.set_speed(speed)
        if self.ena_pin is not None:
            self.ena_pin.on()
        self.in1_pin.value(0)
        self.in2_pin.value(1)

    def stop(self):
        if self.pwm_pin is not None:
            self.pwm_pin.duty(0)
        if self.ena_pin is not None:
            self.ena_pin.value(0)
        self.in1_pin.value(0)
        self.in2_pin.value(0)

    def deinit(self):
        self.stop()
        if self.pwm_pin is not None:
            self.pwm_pin.deinit()
        if self.ena_pin is not None:
            self.ena_pin.deinit()
        self.in1_pin.deinit()
        self.in2_pin.deinit()


'''

左前轮：Left front wheel
右前轮：Right front wheel
左后轮：Left rear wheel
右后轮：Right rear wheel
'''

# 4前 16后 17前 5后
# 左前轮电机
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1 = 17
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2 = 5

# 右前轮电机
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1 = 4 
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2 = 16 

#14 后  27 前  26 前 25 后
# 左后轮电机
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1 = 26
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2 = 25

# 右后轮电机
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1 = 27
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2 = 14


class Car:
    def __init__(self):
        """
        初始化Car类的实例
        """
        # 初始化四个电机控制器
        self.left_front_wheel_motor_controller = MotorController(LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1, LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2)
        self.right_front_wheel_motor_controller = MotorController(RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1, RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2)
        self.left_rear_wheel_motor_controller = MotorController(LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1, LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2)
        self.right_rear_wheel_motor_controller = MotorController(RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1, RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2)

    
    def move_forward(self, speed=50):
        """
        向前移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.forward(speed)
        self.right_front_wheel_motor_controller.forward(speed)
        self.left_rear_wheel_motor_controller.forward(speed)
        self.right_rear_wheel_motor_controller.forward(speed)

    def move_backward(self, speed=50):
        """
        向后移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.backward(speed)
        self.right_front_wheel_motor_controller.backward(speed)
        self.left_rear_wheel_motor_controller.backward(speed)
        self.right_rear_wheel_motor_controller.backward(speed)
        
    def move_leftward(self, speed=50):
        """
        向左移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.backward(speed)
        self.right_front_wheel_motor_controller.forward(speed)
        self.left_rear_wheel_motor_controller.forward(speed)
        self.right_rear_wheel_motor_controller.backward(speed)

    def move_rightward(self, speed=50):
        """
        向右移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.forward(speed)
        self.right_front_wheel_motor_controller.backward(speed)
        self.left_rear_wheel_motor_controller.backward(speed)
        self.right_rear_wheel_motor_controller.forward(speed)
    
    def left_forward(self, speed=50):
        """
        左前方移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.stop()
        self.right_front_wheel_motor_controller.forward(speed)
        self.left_rear_wheel_motor_controller.forward(speed)
        self.right_rear_wheel_motor_controller.stop()

    def right_forward(self, speed=50):
        """
        右前方移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.forward(speed)
        self.right_front_wheel_motor_controller.stop()
        self.left_rear_wheel_motor_controller.stop()
        self.right_rear_wheel_motor_controller.forward(speed)

    def left_backward(self, speed=50):
        """
        左后方移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.backward(speed)
        self.right_front_wheel_motor_controller.stop()
        self.left_rear_wheel_motor_controller.stop()
        self.right_rear_wheel_motor_controller.backward(speed)

    def right_backward(self, speed=50):
        """
        右后方移动
        参数:
            - speed: 移动速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.stop()
        self.right_front_wheel_motor_controller.backward(speed)
        self.left_rear_wheel_motor_controller.backward(speed)
        self.right_rear_wheel_motor_controller.stop()

    def rotate_leftward(self, speed=50):
        """
        向左旋转
        参数:
            - speed: 旋转速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.backward(speed)
        self.right_front_wheel_motor_controller.forward(speed)
        self.left_rear_wheel_motor_controller.backward(speed)
        self.right_rear_wheel_motor_controller.forward(speed)

    def rotate_rightward(self, speed=50):
        """
        向右旋转
        参数:
            - speed: 旋转速度 (默认为50)
        """
        self.left_front_wheel_motor_controller.forward(speed)
        self.right_front_wheel_motor_controller.backward(speed)
        self.left_rear_wheel_motor_controller.forward(speed)
        self.right_rear_wheel_motor_controller.backward(speed)

    def stop(self):
        """
        停止移动
        """
        self.left_front_wheel_motor_controller.stop()
        self.right_front_wheel_motor_controller.stop()
        self.left_rear_wheel_motor_controller.stop()
        self.right_rear_wheel_motor_controller.stop()



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
MQTT_CLIENT_CHECK_MSG_FREQ_MS = 50

RELAY_GPIO_NUM = 33

TRIG_GPIO_NUM = 1
ECHO_GPIO_NUM = 1

ULTRASONIC_DISTANCE_SENSOR_TRIG_GPIO_NUM = 19
ULTRASONIC_DISTANCE_SENSOR_ECHO_GPIO_NUM = 18

# 极限距离，单位 cm
DISTANCE_LIMIT = 15



class CarController():
    def __init__(self):
        self.mqtt_client = None
        self.car = None

        self.wifi_util = None
        self.relay = None
        self.ultrasonic_distance_sensor = None

        # self.distance_event = _thread.Event()  # 距离监测事件对象
        self.distance_thread = None  # 距离监测线程
        self.distance_flag = False  # 距离监测标志变量
        self.distance_lock = _thread.allocate_lock()  # 距离监测锁对象
        self.distance_thread_running = True  # 距离监测线程运行标志

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
        self.car = Car()

        self.relay = Relay(RELAY_GPIO_NUM)
        self.relay.off()


        self.ultrasonic_distance_sensor = UltrasonicDistanceSensor(ULTRASONIC_DISTANCE_SENSOR_TRIG_GPIO_NUM,
                ULTRASONIC_DISTANCE_SENSOR_ECHO_GPIO_NUM
        )
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
        print('topic: {}    meg: {} '.format(topic,msg))
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
                # _thread.resume(self.distance_thread)  # 恢复距离监测线程的执行
                # self.distance_event.set()  # 设置事件，恢复距离监测线程的执行
                #self.distance_flag = True  # 设置标志变量为 True，恢复距离监测线程的执行
                # self.distance_lock.acquire()  # 获取锁，恢复距离监测线程的执行
                # self.distance_lock.release()  # 释放锁
                # self.distance_thread_running = True  # 恢复距离监测线程的执
            elif b'off' == msg:
                self.car.stop()
                self.relay.off()
                # _thread.suspend(self.distance_thread)  # 暂停距离监测线程的执行
                # self.distance_event.clear()  # 清除事件，暂停距离监测线程的执行
                #self.distance_flag = False  # 设置标志变量为 False，暂停距离监测线程的执行
                # self.distance_lock.acquire()  # 获取锁，暂停距离监测线程的执行
                # self.distance_lock.release()  # 释放锁
                # self.distance_thread_running = False  # 暂停距离监测线程的执行
            else:
                self.car.stop()


    def do_work(self):
        front_distance = DISTANCE_LIMIT + 1
        print('front_distance: {}'.format(front_distance))
        try:
            # self.distance_thread = _thread.start_new_thread(self.test_distance_limit, ())  # 启动距离监测线程
            while True:
                front_distance = self.ultrasonic_distance_sensor.do_measure()
                print('front_distance: ',front_distance)
                # 容易测量不准，导致测量距离为负数，所以加上大于0判断，要不会造成卡顿
                if (front_distance > 0) and (front_distance < 50):
                    if (front_distance < DISTANCE_LIMIT) :
                        # 不应该是停止，应该是不能继续前进
                        self.car.move_backward()
                self.mqtt_client.check_msg()
                time.sleep_ms(MQTT_CLIENT_CHECK_MSG_FREQ_MS)
        except MemoryError:
            print("Memory error occurred. Restarting...")
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            sys.exit()
    
    def test_distance_limit(self):
        '''
        description: 测试距离，如果达到极限距离，则停止车辆运动。
        Args:
            distance_limit: 极限距离（单位：厘米）。
        Returns:
            None
        TODO 线程无法随着relay的on和off自动关停，留着后续修改，子线程启动后会无辜停止
        '''
        
        try:
            distance = DISTANCE_LIMIT + 1  # 初始化变量为超出距离限制的值
            while True:
                distance = self.ultrasonic_distance_sensor.do_measure()

                print('distance: ', distance) # 容易测量不准，导致测量距离为负数，所以加上大于0判断
                if (distance < DISTANCE_LIMIT) and (distance > 0):
                    self.car.move_backward()
                time.sleep(0.1)
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.car.stop()

def car_test():

    car_controller = CarController()
    car_controller.do_work()

    
def main():
    car_test()


if __name__ == "__main__":
    main()


