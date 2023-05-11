from machine import Pin
import time


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
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM1=
LEFT_FRONT_WHEEL_MOTOR_GPIO_NUM2=

# 右前轮电机
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM1=
RIGHT_FRONT_WHEEL_MOTOR_GPIO_NUM2=

# 左后轮电机
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM1=
LEFT_REAR_WHEEL_MOTOR_GPIO_NUM2=

# 右后轮电机
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM1=
RIGHT_REAR_WHEEL_MOTOR_GPIO_NUM2=

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

