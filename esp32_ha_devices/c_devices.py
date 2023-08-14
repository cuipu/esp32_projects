'''
Author: cuipu g050505@gmail.com
Date: 2023-05-11 22:03:16
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-08-14 20:47:43
FilePath: \esp32_projects\esp32_ha_devices\c_devices.py
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
    def __init__(self, digital_gpio_num: int):
        # 构建人体红外对象
        self.digital_pin = machine.Pin(digital_gpio_num, Pin.IN)
        self.hander = None

    def is_motion_detected(self):
        """
        检测是否有人体存在

        返回值：
        - True：检测到人体存在
        - False：未检测到人体
        """
        value = self.digital_pin.value()  # 读取数字输出引脚的状态
        return value == 1
  
    def set_hander(self, hander):
        """
        设置终端回调函数，当数字输出引脚状态发生变化时调用该函数

        参数：
        - handler: 终端回调函数，接受一个参数（数字输出引脚的状态）
        - 在MicroPython中，IRQ_RISING是电平升高时触发，而IRQ_FALLING是电平下降时触发
        """
        self.hander = hander
        self.digital_pin.irq(handler=self.hander, trigger=Pin.IRQ_RISING)


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
Date: 2023-04-28 14:22:47
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-01 22:25:51
FilePath: \Demo\MultipleController.py
Description: 多路继电器控制

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

'''
class MultipleController:
    def __init__(self, relay_pins, active_high=True):
        # 初始化继电器引脚
        self.relays = []
        for pin_num in relay_pins:
            pin = Pin(pin_num, Pin.OUT)
            self.relays.append(pin)
        
        # 根据高低电平触发设置默认状态
        if active_high:
            default_state = 0  # 高电平触发时默认关闭
        else:
            default_state = 1  # 低电平触发时默认关闭
            
        self.state = [default_state] * len(relay_pins)
        
        # 记录高低电平触发
        self.active_high = active_high

    def set_relay_state(self, relay_num, state):
        """
        设置继电器状态
        
        Args:
            relay_num (int): 继电器编号（从1开始）
            state (int): 继电器状态，0为关闭，1为打开
        """
        if relay_num < 1 or relay_num > len(self.relays):
            raise ValueError("Invalid relay number")
        
        if self.active_high:
            self.relays[relay_num - 1].value(state)
        else:
            self.relays[relay_num - 1].value(1 - state)
        
        self.state[relay_num - 1] = state
    
    def get_relay_state(self, relay_num):
        """
        获取继电器状态
        
        Args:
            relay_num (int): 继电器编号（从1开始）
        
        Returns:
            int: 继电器状态，0为关闭，1为打开
        """
        if relay_num < 1 or relay_num > len(self.relays):
            raise ValueError("Invalid relay number")
        
        return self.state[relay_num - 1]
    
    def toggle_relay_state(self, relay_num):
        """
        切换继电器状态
        
        Args:
            relay_num (int): 继电器编号（从1开始）
        """
        if relay_num < 1 or relay_num > len(self.relays):
            raise ValueError("Invalid relay number")
        
        state = 1 - self.state[relay_num - 1]
        self.set_relay_state(relay_num, state)
    
    def toggle_all_relays(self):
        """切换所有继电器状态"""
        for i in range(1, len(self.relays) + 1):
            self.toggle_relay_state(i)
    
    def turn_on_all_relays(self):
        """打开所有继电器"""
        for i in range(1, len(self.relays) + 1):
            self.set_relay_state(i, 1)
    
    def turn_off_all_relays(self):
        """关闭所有继电器"""
        for i in range(1, len(self.relays) + 1):
            self.set_relay_state(i, 0)


'''
# 示例用法
relay_pins = [2, 3, 4, 5]  # 假设继电器连接到GPIO引脚2、3、4和5
4 18 17 5
controller = FourRelayController(relay_pins)

# 控制第一个继电器打开
controller.set_relay_state(1, 1)
sleep(1)

# 控制第一个继电器关闭
controller.set_relay_state(1, 0)
'''


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
Date: 2023-04-30 11:24:49
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 17:32:39
FilePath: \Demo\c_photosensitive_sensor.py
Description: 三引脚光敏传感器

硬件：
需要电压：3.3V

注意:
    AO引脚只能接ESP32上面带ADCO输出的
    建议AO接左边引脚，DO接右边引脚

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
class LightSensorThreePin:
    def __init__(self, digital_gpio_num: int):
        """
        初始化光敏电阻类

        参数：
        - digital_gpio_num: 光敏电阻数字输出（DO）连接到的引脚
        """
        # 数字量
        self.digital_pin = Pin(digital_gpio_num, Pin.IN)
        # 只要有变动，就会调用handler回调函数
        self.handler = None

        self.threshold = None

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

    def set_handler(self, handler):
        """
        设置终端回调函数，当数字输出引脚状态发生变化时调用该函数

        参数：
        - handler: 终端回调函数，接受一个参数（数字输出引脚的状态）
        - 在MicroPython中，IRQ_RISING是电平升高时触发，而IRQ_FALLING是电平下降时触发
        """
        self.handler = handler
        self.digital_pin.irq(handler=self.handler, trigger=Pin.IRQ_RISING)
        
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

    def start_work(self):
        # 告诉芯片要开始测试了，不同的板子出发条件不同
        self.trig_pin.value(1)
        time.sleep_us(10)
        self.trig_pin.value(0)

    def measure_distance(self):
        # 告诉芯片要开始测试了，不同的板子出发条件不同
        self.trig_pin.value(1)
        time.sleep_us(10)
        self.trig_pin.value(0)

        pulse_duration = 0
        distance = 0
        pulse_end = 0
        pulse_start = 0
        # 接收回声信号并计算距离
        while self.echo_pin.value() == 0:
            pulse_start = time.ticks_us()

        while self.echo_pin.value() == 1:
            pulse_end = time.ticks_us()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 0.0343 / 2

        return distance

    def do_measure(self):
        
        # 告诉芯片要开始测试了，不同的板子出发条件不同
        self.trig_pin.value(1)
        time.sleep_us(10)
        self.trig_pin.value(0)
        
        t1 = 0
        t2 = 0
        t3 = 0
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
        # distance =  t3 * 340 / 2
        return t3 * 343 / 2
        
'''
Author: cuipu g050505@gmail.com
Date: 2023-04-28 11:58:08
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-30 12:21:43
FilePath: \Demo\c_stepper_motor.py
Description: 进步电机

硬件：
需要电压：5V

还没测试，控制板貌似烧了  - -！

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''

class StepperMotor:

    def __init__(self, a_gpio_num: int, b_gpio_num: int, c_gpio_num: int, d_gpio_num: int):

        self.a_pin = Pin(a_gpio_num, Pin.OUT)
        self.b_pin = Pin(b_gpio_num, Pin.OUT)
        self.c_pin = Pin(c_gpio_num, Pin.OUT)
        self.d_pin = Pin(d_gpio_num, Pin.OUT)

        # 初始化都为0
        self.a_pin .value(0)
        self.b_pin .value(0)
        self.c_pin .value(0)
        self.d_pin .value(0)

        # 使用双向链表结构
        self.stepper_motor_pin_double_link = DLinkList()

        self.stepper_motor_pin_double_link.append(self.a_pin)
        self.stepper_motor_pin_double_link.append(self.b_pin)
        self.stepper_motor_pin_double_link.append(self.c_pin)
        self.stepper_motor_pin_double_link.append(self.d_pin)

    def turn(self, delay_time_ms=100, reverse: int = (0, 1)):

        while not self.stepper_motor_pin_double_link.is_empty():
            cur = self.stepper_motor_pin_double_link._head
            if 1 == reverse:
                cur.item.value(0)
            else:
                cur.item.value(1)

            cur = cur.next
            time.sleep_ms(delay_time_ms)

            if 1 == reverse:
                cur.item.value(1)
            else:
                cur.item.value(0)


class Node(object):
    """双向链表节点"""

    def __init__(self, item):
        self.item = item
        self.next = None
        self.prev = None


class DLinkList(object):
    """双向链表"""

    def __init__(self):
        self._head = None

    def is_empty(self):
        """判断链表是否为空"""
        return self._head == None

    def length(self):
        """返回链表的长度"""
        cur = self._head
        count = 0
        while cur != None:
            count += 1
            cur = cur.next
        return count

    def travel(self):
        """遍历链表"""
        cur = self._head
        while cur != None:
            print(cur.item)
            cur = cur.next
        print("")

    def add(self, item):
        """头部插入元素"""
        node = Node(item)
        if self.is_empty():
            # 如果是空链表，将_head指向node
            self._head = node
        else:
            # 将node的next指向_head的头节点
            node.next = self._head
            # 将_head的头节点的prev指向node
            self._head.prev = node
            # 将_head 指向node
            self._head = node

    def append(self, item):
        """尾部插入元素"""
        node = Node(item)
        if self.is_empty():
            # 如果是空链表，将_head指向node
            self._head = node
        else:
            # 移动到链表尾部
            cur = self._head
            while cur.next != None:
                cur = cur.next
            # 将尾节点cur的next指向node
            cur.next = node
            # 将node的prev指向cur
            node.prev = cur

    def search(self, item):
        """查找元素是否存在"""
        cur = self._head
        while cur != None:
            if cur.item == item:
                return True
            cur = cur.next
        return False

    def insert(self, pos, item):
        """在指定位置添加节点"""
        if pos <= 0:
            self.add(item)
        elif pos > (self.length()-1):
            self.append(item)
        else:
            node = Node(item)
            cur = self._head
            count = 0
            # 移动到指定位置的前一个位置
            while count < (pos-1):
                count += 1
                cur = cur.next
            # 将node的prev指向cur
            node.prev = cur
            # 将node的next指向cur的下一个节点
            node.next = cur.next
            # 将cur的下一个节点的prev指向node
            cur.next.prev = node
            # 将cur的next指向node
            cur.next = node

    def remove(self, item):
        """删除元素"""
        if self.is_empty():
            return
        else:
            cur = self._head
            if cur.item == item:
                # 如果首节点的元素即是要删除的元素
                if cur.next == None:
                    # 如果链表只有这一个节点
                    self._head = None
                else:
                    # 将第二个节点的prev设置为None
                    cur.next.prev = None
                    # 将_head指向第二个节点
                    self._head = cur.next
                return
            while cur != None:
                if cur.item == item:
                    # 将cur的前一个节点的next指向cur的后一个节点
                    cur.prev.next = cur.next
                    # 将cur的后一个节点的prev指向cur的前一个节点
                    cur.next.prev = cur.prev
                    break
                cur = cur.next



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



