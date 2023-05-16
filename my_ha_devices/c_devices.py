'''
Author: cuipu g050505@gmail.com
Date: 2023-05-11 22:03:16
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-14 22:01:48
FilePath: \esp32_projects\my_ha_devices\c_devices.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 22:23:22
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-13 10:59:47
FilePath: \esp32_projects\my_ha_devices\c_devices.py
Description: 有源蜂鸣器，带白纸的，内部有震荡源

硬件：
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
from machine import Pin, SoftI2C, ADC
import machine
import time
import ssd1306
from esp32_i2c_1602lcd import I2cLcd
import ds18x20
import onewire



class ActiveBuzzer:
    def __init__(self, active_buzzer_gpio_num: int, mode: int = 1):
        # mode 控制高低输出方式，不知道为什么，使用machine.Pin运行不起来
        self.active_buzzer_pin = Pin(active_buzzer_gpio_num, Pin.OUT)
        if 1 == mode:
            self.on_value = 1
            self.off_value = 0
        else:
            self.on_value = 0
            self.off_value = 1

    def do_warning_sound(self, times: int = 10):
        for i in range(times):
            self.active_buzzer_pin.value(self.on_value)  # 不响
            time.sleep(0.2)
            self.active_buzzer_pin.value(self.off_value)  # 响
            time.sleep(0.2)
        self.active_buzzer_pin.value(self.off_value)

    def do_always_sound(self):
        while True:
            self.active_buzzer_pin.value(self.on_value)

    def stop_sound(self):
        self.active_buzzer_pin.value(self.off_value)


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 22:43:04
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-05 00:23:06
FilePath: \Demo\c_passive_buzzer.py
Description: 无源蜂鸣器，需要PWM信号，不带白纸的

硬件：
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class PassiveBuzzer:

    def __init__(self, passive_buzzer_gpio_num: int, freq=440):
        # 不知道为什么，使用machine.Pin运行不起来
        self.pin = Pin(passive_buzzer_gpio_num, Pin.OUT)
        # self.pwm = PWM(Pin(pin, Pin.OUT))
        self.pwm = None
        self.freq = freq

    def play_mario(self, wait=150, duty=512):
        # 如果已经在播放，则先停止
        if self.pwm:
            self.stop()
        # 初始化PWM对象，并设置占空比为50%
        # self.pwm = PWM(self.pin, freq=self.freq, duty=512)
        self.pwm = machine.PWM(self.pin, freq=self.freq, duty=512)

        for note in PassiveBuzzerMusic.MARIO:
            if note:
                self.pwm.freq(note)
            self.pwm.duty(duty)
            time.sleep_ms(wait)
        # 暂停PWM，将占空比设置为0
        self.pwm.duty(0)

        self.stop()

    # 停止播放

    def stop(self):
        # 如果没有在播放，则返回
        if not self.pwm:
            return
        # 停止PWM对象
        self.pwm.deinit()
        self.pwm = None

    # 播放指定频率和持续时间的声音
    def tone(self, freq, duration):
        # 如果已经在播放，则先停止
        if self.pwm:
            self.stop()
        # 初始化PWM对象，并设置占空比为50%
        self.pwm = machine.PWM(self.pin, freq=self.freq, duty=512)
        # 播放指定持续时间后停止
        time.sleep_ms(duration)
        self.stop()


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 00:02:03
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 17:55:20
FilePath: \Demo\c_ds18b20_temperature_sensor.py
Description: ds18B20温度传感器

硬件：ds18B20
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class Ds18b20TemperatureSensor:
    def __init__(self, ds_gpio_num: int):
        self.ds_pin = machine.Pin(ds_gpio_num)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.devices = self.ds_sensor.scan()

    def collect_temperature_result(self):
        self.ds_sensor.convert_temp()
        for device in self.devices:
            temp = self.ds_sensor.read_temp(device)
            if isinstance(temp, float):
                temp = round(temp, 2)
                # device = device.decode('utf-8')
                return device, temp
        return 0  # 这里删除，那么默认此函数在没有获取到温度的时候返回为默认值None，调用处判断即可


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-27 21:57:38
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-29 12:39:36
FilePath: \Demo\c_esp32_i2c_1602lcd.py
Description: 

硬件：1602lcd
需要电压：5V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


# SDA GPIO15
# SCL GPIO2
# Vcc 5V （3V显示不清楚）
# GND GND


# 注意修改PCF8574中SAD和SCL的引脚
# SAD_PIN = 15 12
# SCL_PIN = 2 13

DEFAULT_I2C_ADDR = 0x27
DEFAULT_NUM_LINES = 2
DEFAULT_NUM_COLUMNS = 16


class ESP32160lcd:
    def __init__(self, sda_gpio_num: int, scl_gpio_num: int, freq=100000):

        i2c = machine.SoftI2C(sda=machine.Pin(sda_gpio_num),
                              scl=machine.Pin(scl_gpio_num), freq=100000)
        self.lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR,
                          DEFAULT_NUM_LINES, DEFAULT_NUM_COLUMNS)

    '''
    SCL控制时钟
    SAD控制数据
    freq控制频率
    '''
    # 扫描1602lcd的地址号，地址号为十进制的，改为十六进制的前面需要添加0x
    # i2c.scan()
    # 比如扫描出来的是39，改为十六进制 0x27

    '''
    description: 
    param {*} self
    param {*} first_row 第一行显示
    param {*} second_row 第二行显示
    param {float} secs 刷新频率，单位是秒
    return {*}
    '''

    def show_msg(self, first_row: str, second_row: str):
        self.lcd.putstr("{}\n".format(first_row))
        self.lcd.putstr("{}".format(second_row))

    def clear_msg(self):
        self.lcd.clear()


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-30 20:41:30
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-01 22:24:56
FilePath: \Demo\c_infrared_human_sensor.py
Description: 红外人体感应

硬件：HC-SR501
需要电压：5V
接线：
    三个接线柱在下面，左边的是VCC，中间的是IO，右边的是GND
    上面两个黄色的旋钮，左边的是时间延迟调节，右边的是感应距离调节

    右侧上角黄色和接线柱为检测模式条线
    L：为重复
    H：为不重复
    不可重复触发方式：即感应输出高电平后，延时时间段一结束，输出将自动从高电平变成低电平

    可重复触发方式：即感应输出高电平后，在延时时间段内，如果有人体在其感应范围活动，其输出将一直保持高电平，直到人离开后才延时将高电平变为低电平

    最好选择带ADC输出的，也就是左边的引脚
Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class InfraredMotionSensor:
    def __init__(self, sensor_gpio_num: int):
        # 构建人体红外对象
        self.sensor_pin = machine.Pin(sensor_gpio_num, Pin.IN)
        self.hander = None
        
    def set_hander(self, hander, *args):
        self.hander = hander
        self.sensor_pin.irq(handler=self.hander, trigger=Pin.IRQ_RISING)


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 21:53:45
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 16:16:04
FilePath: \Demo\c_matrix_keyboard.py
Description: 矩阵键盘

硬件：
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class MatrixKeyboard:
    def __init__(self, row1_gpio_num: int, row2_gpio_num: int, row3_gpio_num: int, row4_gpio_num: int,
                 col1_gpio_num: int, col2_gpio_num: int, col3_gpio_num: int, col4_gpio_num: int):

        self.row1 = machine.Pin(row1_gpio_num, Pin.OUT)
        self.row2 = machine.Pin(row2_gpio_num, Pin.OUT)
        self.row3 = machine.Pin(row3_gpio_num, Pin.OUT)
        self.row4 = machine.Pin(row4_gpio_num, Pin.OUT)
        self.row_list = [self.row1, self.row2, self.row3, self.row4]

        self.col1 = machine.Pin(col1_gpio_num, Pin.IN, Pin.PULL_DOWN)
        self.col2 = machine.Pin(col2_gpio_num, Pin.IN, Pin.PULL_DOWN)
        self.col3 = machine.Pin(col3_gpio_num, Pin.IN, Pin.PULL_DOWN)
        self.col4 = machine.Pin(col4_gpio_num, Pin.IN, Pin.PULL_DOWN)
        self.col_list = [self.col1, self.col2, self.col3, self.col4]

        self.keyboard_buttons = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]

    def receive_pressed_buttons(self):
        while True:
            pressed_button = ''
            for i, row in enumerate(self.row_list):
                for temp in self.row_list:
                    temp.value(0)
                row.value(1)
                time.sleep_ms(10)
                for j, col in enumerate(self.col_list):
                    if col.value() == 1:
                        pressed_button = self.keyboard_buttons[i][j]
                        return pressed_button

            time.sleep(0.1)


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-30 18:00:11
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 21:53:51
FilePath: \Demo\c_oled_ssd1306_screen.py
Description: OLED屏幕

硬件：
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class MySSD1306:
    def __init__(self, scl_gpio_num, asd_gpio_num, width: int = 128, height: int = 64):
        self.width = width
        self.height = height
        self.i2c = machine.SoftI2C(scl=machine.Pin(scl_gpio_num),
                                   sda=machine.Pin(asd_gpio_num))
        self.ssd1306 = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)

    # 显示三行
    def show_three_row_msg(self, first_row_msg: str = '', second_row_msg: str = '', third_row_msg: str = '', x: int = 0, y: int = 0):

        self.ssd1306.text(first_row_msg, x, y+5)
        self.ssd1306.text(second_row_msg, x, y + 25)
        self.ssd1306.text(third_row_msg, x, y + 45)

        self.ssd1306.show()


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-28 14:22:47
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-01 22:25:51
FilePath: \Demo\c_relay.py
Description: 继电器控制

接线方式：
    DC+：正极/5V 左边
    DC-：负极/GND 中间
    IN：GPIO 右边

    COM：公共端
    NO（normal open 开路）：常开端，就是继电器不通电，这端和COM端是断开的，不连通。通电后，和COM端是连通。
    NC（normal close 闭合）：常闭端，就是继电器不通电，这个端和COM公共端是连通的，触点是闭合的，开关是关闭的。通电后，这端和COM端是断开的

    接 NO 和 COM，不通电时开路，通电时闭合
    接 NC 和 COM，不通电时闭合，通电时开路



硬件：
需要电压：5V

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''


class Relay:
    def __init__(self, repay_gpio_num, trigger_high=True):
        """
        初始化继电器类

        :param pin_num: 继电器控制引脚的引脚号
        :type pin_num: int
        :param trigger_high: 继电器是高电平触发还是低电平触发，默认是高电平触发
        :type trigger_high: bool
        """
        self.relay_pin = Pin(repay_gpio_num, Pin.OUT)
        self.trigger_high = trigger_high

    def on(self):
        """
        继电器打开
        """
        if self.trigger_high:
            self.relay_pin.on()
        else:
            self.relay_pin.off()

    def off(self):
        """
        继电器关闭
        """
        if self.trigger_high:
            self.relay_pin.off()
        else:
            self.relay_pin.on()


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 12:15:50
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-29 12:56:08
FilePath: \Demo\c_shock_sensor.py
Description: 震动传感器

硬件：SW-420
其他产品还有：SW-18010P, SW520D, 801S 没测试
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class ShockSensor:
    def __init__(self, shock_gpio_num: int):
        self.shock_gpio_num = shock_gpio_num
        # 注意：这里需要输入给ESP32信息，所有是Pin.IN，
        self.shock_pin = machine.Pin(shock_gpio_num, Pin.IN)

    def collect_shock_result(self):
        return self.shock_pin.value()


'''
Author: cuipu g050505@gmail.com
Date: 2023-04-30 16:21:51
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-03 10:22:32
FilePath: \Demo\c_sound_sensor.py
Description: 声音传感器

硬件：高感度麦克风传感器模块
需要电压：3.3V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''


class SoundSenser:
    def __init__(self, adc_gpio_num: int, dv_gpio_num: int):
        # 模拟量
        self.adc_pin = ADC(machine.Pin(adc_gpio_num))
        self.adc_pin.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V

        # 数字量
        self.do_pin = machine.Pin(dv_gpio_num, Pin.IN)
        

    def collect_sound_result(self):
        # 获取结果
        adc_result = self.adc_pin.read()  # 0-4095
        light_result = self.do_pin.value()
        return adc_result, light_result

    def set_hander(self, *argc):
        # 只要有变动，就会调用hander回调函数
        self.do_pin.irq(handler=self.hander, trigger=Pin.IRQ_RISING)

'''
Author: cuipu g050505@gmail.com
Date: 2023-04-30 11:24:49
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 17:32:39
FilePath: \Demo\c_photosensitive_sensor.py
Description: 光敏传感器

硬件：
需要电压：3.3V

注意:
    AO引脚只能接ESP32上面带ADCO输出的
    建议AO接左边引脚，DO接右边引脚

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
class LightSensor:
    def __init__(self, analog_gpio_num: int, digital_gpio_num: int):
        """
        初始化光敏电阻类
        
        参数：
        - analog_gpio_num: 光敏电阻模拟输出（AO）连接到的引脚
        - digital_gpio_num: 光敏电阻数字输出（DO）连接到的引脚
        
        注意：
        - analog_pin 参数应该是 ADC 引脚
        """
        # 模拟量
        self.adc_pin = ADC(Pin(analog_gpio_num))
        self.adc_pin.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V

        # 数字量
        self.digital_pin = Pin(digital_gpio_num, Pin.IN)
        # 只要有变动，就会调用hander回调函数
        self.hander = None

        self.threshold = None

    def read_light_analog(self):
        """
        读取光敏电阻的模拟输出（AO）值
        
        返回值：
        - 模拟输出值的数字表示
        """
        value = self.adc_pin.read()  # 读取模拟输出引脚的值
        return value

    def read_light_digital(self):
        """
        读取光敏电阻的数字输出（DO）值
        
        返回值：
        - 数字输出引脚的状态（高电平为1，低电平为0）
        """
        value = self.digital_pin.value()  # 读取数字输出引脚的状态
        return value

    def set_threshold(self, threshold):
        """
        设置光敏电阻的阈值
        
        参数：
        - threshold: 光照强度的阈值
        
        注意：
        - 阈值可以根据实际需求进行调整
        """
        self.threshold = threshold

    def set_hander(self, hander,*args):
        """
        设置终端回调函数，当数字输出引脚状态发生变化时调用该函数
        
        参数：
        - hander: 终端回调函数，接受一个参数（数字输出引脚的状态）
        - Pin.IRQ_RISING电平升高时触发
        """
        self.hander = hander
        self.digital_pin.irq(handler=self.hander, trigger=Pin.IRQ_RISING)
        
'''
Author: cuipu g050505@gmail.com
Date: 2023-05-02 22:28:26
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-03 10:01:37
FilePath: \Demo\c_ultrasonic_meter.py
Description: 超声波测距仪

硬件: HC-SR04
需要电压：5.0V

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''

"""
echo脚会由0变为1此时MCU开始计时，当超声波模块接收到返回的声波时，echo由1变为0此时MCU停止计时
然后再通过声音的传输速度是340m/s就可以计算出距离，切记要除以2，毕竟声音是来回的距离
"""

class UltrasonicDistanceSensor:
    def __init__(self, trig_gpio_num: int, echo_gpio_num: int):

        self.trig_pin = Pin(trig_gpio_num, Pin.OUT)
        self.echo_pin = Pin(echo_gpio_num, Pin.IN)
        self.trig_pin.value(0)
        self.echo_pin.value(0)

    def do_measure(self):
        # 告诉芯片要开始测试了，不同的板子出发条件不同
        self.trig_pin.value(1)
        time.sleep_us(10)
        self.trig_pin.value(0)

        # 检测回响信号，为低电平时，测距完成
        while self.echo_pin.value() == 0:
            # 开始不断递增的微秒计数器 1
            t1 = time.ticks_us()
        # 检测回响信号，为高电平时，测距开始
        while self.echo_pin.value() == 1:
            # 开始不断递增的微秒计数器 2
            t2 = time.ticks_us()

        # 计算两次调用 ticks_ms(), ticks_us(), 或 ticks_cpu()之间的时间，这里是ticks_us()
        # 这时间差就是测距总时间，在乘声音的传播速度340米/秒，除2就是距离
        # 例如 t2-t1=12848此时单位是us，转换为秒就是12848 / 1000000 此时单位是秒，此时如果乘以340计算出的单位是米，
        # 然后再乘以100就是厘米，因此，直接 用12848/10000即可
        t3 = time.ticks_diff(t2, t1) / 10000

        # 这里返回的是：开始测距的时间减测距完成的时间*声音的速度/2（来回）
        return t3 * 340 / 2



# 音符与对应的的频率
class PassiveBuzzerMusic():
    B0 = 31
    C1 = 33
    CS1 = 35
    D1 = 37
    DS1 = 39
    E1 = 41
    F1 = 44
    FS1 = 46
    G1 = 49
    GS1 = 52
    A1 = 55
    AS1 = 58
    B1 = 62
    C2 = 65
    CS2 = 69
    D2 = 73
    DS2 = 78
    E2 = 82
    F2 = 87
    FS2 = 93
    G2 = 98
    GS2 = 104
    A2 = 110
    AS2 = 117
    B2 = 123
    C3 = 131
    CS3 = 139
    D3 = 147
    DS3 = 156
    E3 = 165
    F3 = 175
    FS3 = 185
    G3 = 196
    GS3 = 208
    A3 = 220
    AS3 = 233
    B3 = 247
    C4 = 262
    CS4 = 277
    D4 = 294
    DS4 = 311
    E4 = 330
    F4 = 349
    FS4 = 370
    G4 = 392
    GS4 = 415
    A4 = 440
    AS4 = 466
    B4 = 494
    C5 = 523
    CS5 = 554
    D5 = 587
    DS5 = 622
    E5 = 659
    F5 = 698
    FS5 = 740
    G5 = 784
    GS5 = 831
    A5 = 880
    AS5 = 932
    B5 = 988
    C6 = 1047
    CS6 = 1109
    D6 = 1175
    DS6 = 1245
    E6 = 1319
    F6 = 1397
    FS6 = 1480
    G6 = 1568
    GS6 = 1661
    A6 = 1760
    AS6 = 1865
    B6 = 1976
    C7 = 2093
    CS7 = 2217
    D7 = 2349
    DS7 = 2489
    E7 = 2637
    F7 = 2794
    FS7 = 2960
    G7 = 3136
    GS7 = 3322
    A7 = 3520
    AS7 = 3729
    B7 = 3951
    C8 = 4186
    CS8 = 4435
    D8 = 4699
    DS8 = 4978

    # 第一首，超级马里奥乐谱
    MARIO = [
        E7, E7, 0, E7, 0, C7, E7, 0,
        G7, 0, 0, 0, G6, 0, 0, 0,
        C7, 0, 0, G6, 0, 0, E6, 0,
        0, A6, 0, B6, 0, AS6, A6, 0,
        G6, E7, 0, G7, A7, 0, F7, G7,
        0, E7, 0, C7, D7, B6, 0, 0,
        C7, 0, 0, G6, 0, 0, E6, 0,
        0, A6, 0, B6, 0, AS6, A6, 0,
        G6, E7, 0, G7, A7, 0, F7, G7,
        0, E7, 0, C7, D7, B6, 0, 0,
    ]

    # 第二首，jingle bells
    JINGLE_BELLS = [
        E7, E7, E7, 0,
        E7, E7, E7, 0,
        E7, G7, C7, D7, E7, 0,
        F7, F7, F7, F7, F7, E7, E7, E7, E7, D7, D7, E7, D7, 0, G7, 0,
        E7, E7, E7, 0,
        E7, E7, E7, 0,
        E7, G7, C7, D7, E7, 0,
        F7, F7, F7, F7, F7, E7, E7, E7, G7, G7, F7, D7, C7, 0
    ]



