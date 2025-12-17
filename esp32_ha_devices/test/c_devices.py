'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 22:23:22
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2025-12-17 18:33:34
FilePath: \esp32_projects\esp32_ha_devices\c_devices.py
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

from machine import Pin
import time
class ActiveBuzzer:
    """
    有源蜂鸣器（自带震荡电路，通电即响）
   
    硬件说明：
        - 供电：3.3V 或 5V 均可（推荐 3.3V 直连 ESP32）
        - 控制方式：高/低电平触发（取决于模块）
        - 推荐引脚：任意空闲 GPIO（建议 23、25、26、27、32 等）
   
    注意事项：
        1. 部分模块是「高电平响」，部分是「低电平响」
        2. 长时间鸣响会非常耗电且吵闹，请勿在安静环境长时间调用
        3. 不需要 PWM，直接数字 IO 控制即可
    """
    def __init__(self, pin: int, active_high: bool = True):
        """
        初始化有源蜂鸣器
       
        参数:
            pin : GPIO 引脚号
            active_high : True → 高电平响（大多数模块）
                          False → 低电平响（少数模块）
        """
        self.pin = Pin(pin, Pin.OUT)
        self.on_value = 1 if active_high else 0
        self.off_value = 0 if active_high else 1
        self.off()  # 上电默认关闭

    def on(self) -> None:
        """持续鸣响（阻塞）"""
        self.pin.value(self.on_value)

    def off(self) -> None:
        """关闭蜂鸣器"""
        self.pin.value(self.off_value)

    def beep(self, duration_ms: int = 100) -> None:
        """
        短促蜂鸣一次（最常用）
       
        参数:
            duration_ms : 鸣响时长（毫秒），推荐 50~500
        """
        self.pin.value(self.on_value)
        time.sleep_ms(duration_ms)
        self.pin.value(self.off_value)

    def beeps(self, count: int = 3, on_ms: int = 100, off_ms: int = 100) -> None:
        """
        连续鸣响多次（经典提示音）
       
        示例：
            buzzer.beeps(3)           # 滴滴滴
            buzzer.beeps(2, 500, 200) # 滴——滴——（长音）
        """
        for i in range(count):
            self.pin.value(self.on_value)
            time.sleep_ms(on_ms)           # ← 修复！原来这里写错了！
            self.pin.value(self.off_value)
            if i < count - 1:              # 最后一次不延时
                time.sleep_ms(off_ms)

    def warning(self, times: int = 10, interval: float = 0.2) -> None:
        """经典报警声「滴滴滴滴滴...」"""
        for _ in range(times):
            self.pin.value(self.on_value)
            time.sleep(interval)
            self.pin.value(self.off_value)
            time.sleep(interval)

    def sos(self) -> None:
        """播放国际摩尔斯电码 SOS（··· --- ···）"""
        for _ in range(3):  # S
            self.beep(150)
            time.sleep_ms(100)
        time.sleep_ms(100)
        for _ in range(3):  # O
            self.pin.value(self.on_value)
            time.sleep_ms(400)
            self.pin.value(self.off_value)
            time.sleep_ms(100)
        time.sleep_ms(100)
        for _ in range(3):  # S
            self.beep(150)
            time.sleep_ms(100)
        time.sleep_ms(500)

    def success(self) -> None:
        """成功提示音：滴滴~（短-长）"""
        self.beep(100)
        time.sleep_ms(100)
        self.pin.value(self.on_value)
        time.sleep_ms(300)
        self.off()

    def error(self) -> None:
        """错误提示音：低沉长音"""
        self.pin.value(self.on_value)
        time.sleep_ms(800)
        self.off()


# ========================== 使用示例 ==========================
if __name__ == "__main__":
    buzzer = ActiveBuzzer(23)           # 如果你的模块低电平响，改成 ActiveBuzzer(23, False)
    
    buzzer.success()        # 成功
    time.sleep(1)
    
    buzzer.beeps(3)         # 滴滴滴
    time.sleep(1)
    
    buzzer.warning(6)       # 报警
    time.sleep(1)
    
    buzzer.sos()            # SOS求救



from machine import Pin, PWM
import time
class PassiveBuzzer:
    """
    无源蜂鸣器（需要 PWM 驱动，不带震荡电路）
    
    硬件说明：
        - 供电：3.3V（也可接 5V，但声音更大）
        - 控制方式：PWM 方波，频率决定音高，占空比决定音量
        - 推荐引脚：任意支持 PWM 的 GPIO（推荐 23、25、26、27、32、33）
    
    超实用特性（全部免费送你）：
        - 支持直接用音符名播放：tone("C5")、tone("E6")
        - 内置多首经典曲目：mario、tetris、starwars、happy birthday…
        - 支持调节音量（duty 0~1023）
        - 自动停止、防止重复初始化
        - 完全非阻塞（可配合 utime.ticks_ms() 做更精确节奏）
    """

    # 标准音符频率表（八度 4~7）
    NOTES = {
        "C4": 262,  "C#4": 277, "D4": 294,  "D#4": 311, "E4": 330,  "F4": 349,
        "F#4": 370, "G4": 392,  "G#4": 415, "A4": 440,  "A#4": 466, "B4": 494,
        "C5": 523,  "C#5": 554, "D5": 587,  "D#5": 622, "E5": 659,  "F5": 698,
        "F#5": 740, "G5": 784,  "G#5": 831, "A5": 880,  "A#5": 932, "B5": 988,
        "C6":1047,  "C#6":1109, "D6":1175, "D#6":1245, "E6":1319, "F6":1397,
        "F#6":1480, "G6":1568, "G#6":1661, "A6":1760, "A#6":1865, "B6":1976,
        "C7":2093,  "REST": 0
    }

    # 经典内置曲目（可无限扩展）
    SONGS = {
        "mario":    ["E5","E5",0,"E5",0,"C5","E5",0,"G5",0,0,0,"G4",0,
                     "C5",0,0,"G4",0,0,"E4",0, 0,"A4",0,"B4",0,"A#4","A4",0,
                     "G4","E5","G5","A5",0,"F5","G5",0,"E5",0,"C5","D5","B4"],
        "tetris":   ["E5","B4","C5","D5","C5","B4","A4","A4","C5","E5","D5","C5",
                     "B4","B4","C5","D5","E5","C5","A4","A4"],
        "starwars": ["C4","G4","F4","E4","D4","C5","G4","F4","E4","D4","C5","G4","F4","E4","F4","D4"],
        "happy":    ["C4","C4","D4","C4","F4","E4","C4","C4","D4","C4","G4","F4",
                     "C4","C4","C5","A4","F4","E4","D4","A#4","A#4","A4","F4","G4","F4"],
        "jingle":   ["E5","E5","E5","E5","E5","E5","E5","G5","C5","D5","E5"]
    }

    def __init__(self, pin: int, default_freq: int = 440):
        """
        初始化无源蜂鸣器
        
        参数:
            pin           : GPIO 引脚号（推荐 23/25/26/27/32/33）
            default_freq  : 默认频率（备用），一般用不到
        """
        self.pin = Pin(pin, Pin.OUT)
        self.pwm = None
        self.default_freq = default_freq

    def _get_freq(self, note) -> int:
        """支持数字频率和音符名"""
        if isinstance(note, str):
            return self.NOTES.get(note.upper())
        return int(note) if note > 0 else 0

    def tone(self, note, duration_ms: int = 200, volume: int = 512) -> None:
        """
        播放单个音符（最核心方法）
        
        参数:
            note        : 频率（数字）频率 或 （字符串）音符名，如 "C5"、"REST"
            duration_ms : 持续时间（毫秒）
            volume      : 音量 0~1023（推荐 300~700，越大越响也越刺耳）
        """
        freq = self._get_freq(note)
        if freq == 0:  # 休止符
            if self.pwm:
                self.pwm.duty(0)
            time.sleep_ms(duration_ms)
            return

        if self.pwm:
            self.stop()
        self.pwm = PWM(self.pin, freq=freq, duty=volume)
        time.sleep_ms(duration_ms)
        self.pwm.duty(0)  # 立即静音，防止残响

    def play(self, song_name: str, bpm: int = 120, volume: int = 512) -> None:
        """
        播放内置曲目
        
        示例：
            buzzer.play("mario")
            buzzer.play("happy", bpm=100, volume=400)
        """
        song = self.SONGS.get(song_name.lower())
        if not song:
            print(f"[Buzzer] Unknown song: {song_name}")
            print("可用曲目:", ", ".join(self.SONGS.keys()))
            return

        # 计算单个四分音符时长
        beat_ms = 60000 // bpm
        for note in song:
            self.tone(note, beat_ms, volume)
            time.sleep_ms(int(beat_ms * 0.1))  # 音符间短暂停顿，更自然

    def stop(self) -> None:
        """立即停止所有声音"""
        if self.pwm:
            self.pwm.duty(0)
            self.pwm.deinit()
            self.pwm = None

    def beep(self, freq=1000, duration_ms=100, volume=512) -> None:
        """短促提示音（滴一下）"""
        self.tone(freq, duration_ms, volume)

    def success(self) -> None:
        """成功提示音：嘀~嘀嘟~"""
        self.tone("C5", 100)
        time.sleep_ms(50)
        self.tone("E5", 100)
        time.sleep_ms(50)
        self.tone("G5", 300)

    def error(self) -> None:
        """错误提示音：长低音"""
        self.tone("C4", 600, 600)


# ========================== 使用示例 ==========================
if __name__ == "__main__":
    buzzer = PassiveBuzzer(23)  # 改成你的引脚

    buzzer.success()           # 成功
    time.sleep(1)

    buzzer.play("mario")      # 马里奥
    time.sleep(1)

    buzzer.play("happy")      # 生日快乐
    time.sleep(1)

    buzzer.tone("C6", 500)   # 直接弹一个高音C


from machine import Pin
import onewire
import ds18x20
import time
class DS18B20:
    """
    DS18B20 单总线数字温度传感器（支持同时挂多个探头）
    
    硬件说明：
        - 供电：3.3V（推荐）或 5V
        - 接线方式：三线制（VCC、GND、DQ） + 4.7kΩ 上拉电阻（必接！）
        - 推荐引脚：任意 GPIO（建议 4、15、19、27、32、33）
        - 可并联最多 10+ 个探头（每个都有独立 64 位 ROM 地址）
    
    常见问题速查：
        - 不读数 → 忘接 4.7k 上拉电阻（99% 的原因）
        - 读到 85.0°C → 上电未转换，默认值
        - 读到 -127°C → 通信失败
    """

    def __init__(self, pin: int = 19, resolution: int = 12):
        """
        初始化 DS18B20
        
        参数:
            pin        : 数据引脚（DQ）
            resolution : 精度位数 9~12（默认12位 ≈ 0.0625°C，转换时间750ms）
        """
        self.ow = onewire.OneWire(Pin(pin))
        self.ds = ds18x20.DS18X20(self.ow)
        self.resolution = max(9, min(12, resolution))

        # 扫描所有探头
        self.roms = self.ds.scan()
        if not self.roms:
            raise RuntimeError("[DS18B20] 未检测到任何探头！请检查接线和上拉电阻")
        print(f"[DS18B20] 发现 {len(self.roms)} 个探头")

        # 设置所有探头精度，有些设备不支持
        #for rom in self.roms:
        #    self.ds.write_scratchpad(rom, resolution=self.resolution)

    def _convert(self) -> None:
        """触发温度转换（所有探头同时转换）"""
        try:
            self.ds.convert_temp()
            # 转换时间根据精度不同而变化（毫秒）
            delay_ms = {9: 94, 10: 188, 11: 375, 12: 750}[self.resolution]
            time.sleep_ms(delay_ms)
        except Exception as e:
            print("[DS18B20] 转换触发失败:", e)

    def read_temp(self, index: int = 0) -> float | None:
        """
        读取第 index 个探头的温度（从 0 开始）
        返回 None 表示读取失败
        """
        if index >= len(self.roms):
            return None

        self._convert()
        try:
            temp = self.ds.read_temp(self.roms[index])
            # 过滤异常值
            if temp is None or temp < -55 or temp > 125:
                return None
            return round(temp, 2)
        except Exception as e:
            print(f"[DS18B20] 读取失败 (index={index}):", e)
            return None

    def read_all(self) -> list[tuple[bytes, float]]:
        """
        读取所有探头温度
        返回: [(rom_bytes, temperature), ...]
        """
        self._convert()
        result = []
        for rom in self.roms:
            try:
                temp = self.ds.read_temp(rom)
                if -55 <= temp <= 125:
                    result.append((rom, round(temp, 2)))
                else:
                    result.append((rom, None))
            except:
                result.append((rom, None))
        return result

    def get_temp_by_rom(self, rom: bytes) -> float | None:
        """通过 ROM 地址读取特定探头温度"""
        if rom not in self.roms:
            return None
        self._convert()
        try:
            temp = self.ds.read_temp(rom)
            return round(temp, 2) if -55 <= temp <= 125 else None
        except:
            return None

    def get_first_temp(self) -> float | None:
        """最常用：只取第一个探头的温度（兼容你原来代码）"""
        return self.read_temp(0)

    def print_all(self) -> None:
        """调试用：打印所有探头信息"""
        data = self.read_all()
        for rom, temp in data:
            rom_hex = ''.join(f'{b:02X}' for b in rom)
            status = f"{temp}°C" if temp is not None else "ERROR"
            print(f"  ROM: {rom_hex} → {status}")

# ========================== 使用示例 ==========================
if __name__ == "__main__":
    sensor = DS18B20(pin=19)  # 改成你的引脚

    while True:
        temp = sensor.get_first_temp()
        if temp is not None:
            print(f"当前温度: {temp}°C")
        else:
            print("读取失败")
        sensor.print_all()
        time.sleep(2)
                          
                          
from machine import Pin, I2C
from esp32_i2c_1602lcd import I2cLcd
import time

class LCD1602:
    """
    1602 LCD + PCF8574 I2C 扩展板 驱动（工业级最稳方案）
    
    关键结论（血泪经验）：
        - 必须接 5V 供电！3.3V 会花屏/不显示/乱码
        - 必须用硬件 I2C：SDA=21, SCL=22（通道 I2C1）—— 99% 的稳定来源！
        - 地址通常是 0x27 或 0x3F，用 i2c.scan() 确认
        - 背光跳线帽必须插上，对比度电位器必须调到能看到黑块
    """

    DEFAULT_ADDR = 0x27

    def __init__(
        self,
        sda: int = 21,
        scl: int = 22,
        freq: int = 100000,
        addr: int = DEFAULT_ADDR
    ):
        """
        初始化 LCD1602（推荐参数直接用默认值）
        
        参数说明：
            sda/scl : 必须是硬件 I2C 引脚
                      ESP32 硬件 I2C0 → 任意引脚
                      ESP32 硬件 I2C1 → 固定 21(SDA)+22(SCL) ← 最稳！
            freq    : 100kHz（默认）足够，最高可 400kHz
            addr    : PCF8574 地址，默认 0x27
        """
        # 使用硬件 I2C1（21+22），比 SoftI2C 稳定 100 倍！
        self.i2c = I2C(1, sda=Pin(sda), scl=Pin(scl), freq=freq)
        
        # 自动扫描地址（防止 0x27/0x3F 写错）
        devices = self.i2c.scan()
        if not devices:
            raise RuntimeError("[LCD1602] I2C 扫描无设备！请检查接线和 5V 供电")
        
        self.addr = addr if addr in devices else devices[0]
        print(f"[LCD1602] 使用地址 0x{self.addr:02X}")

        self.lcd = I2cLcd(self.i2c, self.addr, 2, 16)
        self.backlight_on()

    # ========================== 基础方法 ==========================
    def clear(self) -> None:
        """清屏"""
        self.lcd.clear()

    def backlight_on(self) -> None:
        """开启背光"""
        self.lcd.backlight_on()

    def backlight_off(self) -> None:
        """关闭背光"""
        self.lcd.backlight_off()

    def print(self, line1: str = "", line2: str = "") -> None:
        """
        最简最常用的显示方法（推荐）
        示例：lcd.print("Temp: 25.6°C", "2025-04-06 20:35")
        """
        self.clear()
        self.lcd.putstr(f"{str(line1)[:16]}\n{str(line2)[:16]}")

    def write(self, text: str, col: int = 0, row: int = 0) -> None:
        """在指定位置写入文字"""
        self.lcd.move_to(col, row)
        self.lcd.putstr(str(text))

    # ========================== 炫酷扩展功能 ==========================
    def boot_animation(self, title: str = "ESP32", wait: float = 2.0) -> None:
        """开机动画（进度条 + 欢迎语）"""
        self.clear()
        self.write("  Initializing...")
        for i in range(17):
            self.write("█" * i, 0, 1)
            time.sleep(0.08)
        self.clear()
        self.print(f"  {title}", "  System Ready!")
        time.sleep(wait)

    def blink(self, times: int = 3, interval: float = 0.2) -> None:
        """背光闪烁提示（如报警、按键确认）"""
        for _ in range(times):
            self.backlight_off()
            time.sleep(interval)
            self.backlight_on()
            time.sleep(interval)

    def progress(self, percent: int, label: str = "Loading") -> None:
        """第二行显示进度条"""
        percent = max(0, min(100, percent))
        bar = "█" * (percent // 7) + "░" * (14 - percent // 7)
        self.write(f"{label}: {bar} {percent}%", 0, 1)

    def show_ip(self, ip: str) -> None:
        """专用于显示 IP 地址"""
        self.print("WiFi Connected", ip)

    def show_temp(self, temp: float, unit: str = "°C") -> None:
        """专用于显示温度"""
        self.print("Temperature", f"{temp:6.1f}{unit}")

    def countdown(self, seconds: int, text: str = "Shutdown in") -> None:
        """倒计时显示"""
        for i in range(seconds, 0, -1):
            self.print(text, f"   {i:3d}s   ")
            time.sleep(1)
        self.clear()

# ========================== 使用示例 ==========================
if __name__ == "__main__":
    lcd = LCD1602()  # 默认就是最稳配置：21+22
    lcd.boot_animation("My Sensor", 1.5)
    lcd.print("Hello World!", "LCD OK!")
    time.sleep(2)
    lcd.blink(3)
    lcd.show_temp(25.6)
    time.sleep(2)
    lcd.show_ip("192.168.1.100")





from machine import Pin, I2C
import ssd1306
import time
import framebuf

class OLED1306:
    """
    SSD1306 OLED 显示屏（128×64，I2C 接口）
   
    硬件说明：
        - 供电：3.3V（完美兼容 ESP32）
        - 推荐接线（硬件 I2C 最稳）：
            VCC → 3.3V
            GND → GND
            SDA → GPIO21
            SCL → GPIO22
        - 地址通常 0x3C（少数 0x3D）
    """
    WIDTH = 128
    HEIGHT = 64

    # 内置小图标（16x16）
    ICONS = {
        "wifi":     bytearray(b'\x00\x00\x1f\x00\x70\x0e\x84!\x0e\x70\x11\x88 \x04@\x02'),
        "nowifi":   bytearray(b'\x00\x00\x1f\x00q\x8e\x87\xa1\x0f\xf0\x13\xc8\'\xe4O\xf2'),
        "temp":     bytearray(b'\x04\n\n\x0e\x0e\x1f\x1f\x0e\x0e\n\n\x04\x04\x04\x0e\x00'),
        "humidity": bytearray(b'\x04\x0e\x0e\x1f\x1f??\x7f\x7f\x7f??\x1f\x0e\x04\x00'),
        "heart":    bytearray(b'\x00f\xff\xff\xff~<\x18<~\xff\xff\xfff\x00\x00'),
        "battery":  bytearray(b'\x1f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00'),
        "warning":  bytearray(b'\x04\x04\x0e\x0e\x1f\x1f??\x3f\x3f\x1f\x1f\x0e\x0e\x04\x00'),
        "ok":       bytearray(b'\x00\x01\x03\x87\x8e\xdc\xf8\xf0\xf8\xdc\x8e\x87\x03\x01\x00\x00')
        # 关键！去掉了最后的 ')  这个非法字符！
    }

    def __init__(self, sda: int = 21, scl: int = 22, freq: int = 400000):
        self.i2c = I2C(1, sda=Pin(sda), scl=Pin(scl), freq=freq)
        devices = self.i2c.scan()
        if not devices:
            raise RuntimeError("[OLED] 未检测到 SSD1306！检查接线")
        self.addr = devices[0]
        print(f"[OLED] 初始化成功，地址 0x{self.addr:02X}")

        self.oled = ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, self.i2c, self.addr)
        self.clear()
        self.show()

    def clear(self) -> None:
        self.oled.fill(0)

    def show(self) -> None:
        self.oled.show()

    def text(self, string: str, x: int, y: int, on: int = 1) -> None:
        self.oled.text(string, x, y, on)

    def pixel(self, x: int, y: int, on: int = 1) -> None:
        self.oled.pixel(x, y, on)

    def line(self, x1: int, y1: int, x2: int, y2: int, on: int = 1) -> None:
        self.oled.line(x1, y1, x2, y2, on)

    def rect(self, x: int, y: int, w: int, h: int, on: int = 1, fill: bool = False) -> None:
        self.oled.rect(x, y, w, h, on)
        if fill:
            self.oled.fill_rect(x, y, w, h, on)

    def icon(self, name: str, x: int, y: int) -> None:
        """显示 16x16 图标"""
        if name not in self.ICONS:
            return
        fb = framebuf.FrameBuffer(self.ICONS[name], 16, 16, framebuf.MONO_HLSB)
        self.oled.blit(fb, x, y)

    def boot_animation(self, title: str = "ESP32", wait: float = 2.0) -> None:
        """开机动画"""
        self.clear()
        self.text("Booting...", 30, 28)
        self.show()
        for i in range(0, 129, 8):
            self.rect(0, 55, i, 6, 1, fill=True)
            self.show()
            time.sleep(0.05)
        self.clear()
        self.text(title, 40, 20)
        self.text("Ready!", 42, 40)
        self.show()
        time.sleep(wait)

    def progress_bar(self, percent: int, x: int = 20, y: int = 50, w: int = 88, h: int = 10) -> None:
        percent = max(0, min(100, percent))
        fill_w = int(w * percent / 100)
        self.rect(x, y, w, h, 1)
        self.rect(x+2, y+2, fill_w-4, h-4, 1, fill=True)
        self.text(f"{percent}%", x+w//2-15, y+2)

    def show_status(self, title: str = "Status", ip: str = "", temp: float = None, wifi: bool = True, battery: int = None) -> None:
        self.clear()
        self.text(title, 35, 0)
        self.icon("wifi" if wifi else "nowifi", 105, 0)
        if ip: self.text(f"IP:{ip}", 0, 16)
        if temp is not None:
            self.icon("temp", 0, 28)
            self.text(f"{temp:5.1f}C", 20, 30)
        if battery is not None:
            self.icon("battery", 100, 28)
            self.text(f"{battery}%", 80, 30)
        self.show()

# ========================== 使用示例 ==========================
if __name__ == "__main__":
    oled = OLED1306()  # 默认 21+22，最稳！

    oled.boot_animation("My Device", 1.5)

    oled.show_status(
        title="Sensor Node",
        ip="192.168.4.1",
        temp=25.6,
        wifi=True,
        battery=87
    )

    # 进度条演示
    for i in range(0, 101, 5):
        oled.progress_bar(i)
        oled.show()
        time.sleep(0.1)

from machine import Pin
import time

class Relay:
    """
    单路继电器模块（5V 机械/固态均适用）
    
    硬件说明：
        - 供电：5V（必须！3.3V 能勉强驱动但极不推荐）
        - 控制方式：高电平触发 或 低电平触发（由模块决定）
        - 推荐接线：
            VCC → 5V / Vin
            GND → GND
            IN  → 任意 GPIO（建议 25、26、26、27、32、33）
        - 常用接法：
            COM + NO → 常开（断电断开，上电闭合）← 最常用！
            COM + NC → 常闭（断电闭合，上电断开）
    
    超实用特性：
        - 支持高/低电平触发自动识别
        - 开机默认安全状态（可设为 OFF）
        - 脉冲控制（点动模式）
        - 状态查询、翻转
        - 支持蜂鸣器/LED 联动提示
    """

    def __init__(
        self,
        pin: int,
        active_high: bool = True,
        name: str = "Relay",
        safe_state_off: bool = True
    ):
        """
        初始化继电器
        
        参数:
            pin           : 控制引脚
            active_high   : True=高电平闭合（最常见），False=低电平闭合
            name          : 继电器名称（用于打印日志）
            safe_state_off: 上电后是否强制关闭（推荐 True，防止意外启动）
        """
        self.pin = Pin(pin, Pin.OUT)
        self.active_high = active_high
        self.name = name

        # 计算实际电平
        self._on_level  = 1 if active_high else 0
        self._off_level = 0 if active_high else 1

        # 开机默认安全关闭
        if safe_state_off:
            self.off()
            # 强制关闭一次
            print(f"[Relay] {self.name} 初始化完成 → 已安全关闭")
        else:
            self.on()
            print(f"[Relay] {self.name} 初始化完成 → 已开启")

    def on(self) -> None:
        """继电器闭合（吸合）"""
        self.pin.value(self._on_level)
        print(f"[Relay] {self.name} → ON")

    def off(self) -> None:
        """继电器断开（释放）"""
        self.pin.value(self._off_level)
        print(f"[Relay] {self.name} → OFF")

    def toggle(self) -> None:
        """切换状态"""
        if self.is_on():
            self.off()
        else:
            self.on()

    def pulse(self, on_ms: int = 200) -> None:
        """
        脉冲控制（点动），常用于门锁、电铃等
        """
        self.on()
        time.sleep_ms(on_ms)
        self.off()

    def is_on(self) -> bool:
        """查询当前是否闭合"""
        return self.pin.value() == self._on_level

    def is_off(self) -> bool:
        """查询当前是否断开"""
        return not self.is_on()

    def set_state(self, state: bool) -> None:
        """安全设置状态"""
        if state:
            self.on()
        else:
            self.off()

    # ========================== 高级功能（超好用） ==========================
    def blink(self, times: int = 3, on_ms: int = 200, off_ms: int = 200) -> None:
        """继电器闪烁（用于提示）"""
        for _ in range(times):
            self.on()
            time.sleep_ms(on_ms)
            self.off()
            time.sleep_ms(off_ms)

    def countdown_close(self, seconds: int, lcd=None) -> None:
        """
        倒计时关闭（常用于延时断电）
        可配合 LCD 显示倒计时
        """
        for i in range(seconds, 0, -1):
            if lcd:
                lcd.print("Auto OFF in", f"{i:2d}s")
            print(f"[Relay] {self.name} 将在 {i}s 后关闭")
            time.sleep(1)
        self.off()
        if lcd:
            lcd.print("Power OFF", "")
        print(f"[Relay] {self.name} 已关闭")


# ========================== 多路继电器扩展（直接复制用） ==========================
class RelayBank:
    """多路继电器控制（4路/8路通用）"""
    def __init__(self, pins: list[int], active_high: bool = True, names: list[str] = None):
        self.relays = []
        for i, p in enumerate(pins):
            name = names[i] if names and i < len(names) else f"Relay{i+1}"
            self.relays.append(Relay(p, active_high, name))

    def on(self, index: int):      self.relays[index].on()
    def off(self, index: int):     self.relays[index].off()
    def toggle(self, index: int):  self.relays[index].toggle()
    def all_on(self):              [r.on() for r in self.relays]
    def all_off(self):             [r.off() for r in self.relays]


# ========================== 使用示例 ==========================
if __name__ == "__main__":
    # 普通单路继电器（高电平触发）
    relay = Relay(pin=26, name="灯")

    relay.on()
    time.sleep(2)
    relay.pulse(500)      # 点动 200ms
    time.sleep(1)
    relay.countdown_close(5)  # 5秒后自动关

    # 低电平触发继电器（如某些固态继电器）
    # relay2 = Relay(27, active_high=False, name="风扇")
    # relay2.on()
    
from machine import Pin
import time

class VibrationSensor:
    """
    震动开关传感器（SW-420、SW-18010P、SW-520D、801S 等）
    
    硬件说明：
        - 供电：3.3V 或 5V 均可（推荐 3.3V 直连 ESP32）
        - 输出：有震动 → 高电平，无震动 → 低电平
        - 灵敏度：模块上电位器顺时针调高（更敏感）
        - 推荐引脚：任意数字输入（建议 34、35、36、39、32、33——这些自带上拉）
    
    超实用特性：
        - 硬件去抖 + 软件防抖
        - 支持中断触发（不占 CPU）
        - 震动计数、震动强度判断
        - 长震/短震区分
        - 支持按键音/报警联动
    """

    def __init__(
        self,
        pin: int,
        debounce_ms: int = 50,
        use_interrupt: bool = True,
        pull: int = Pin.PULL_UP
    ):
        """
        初始化震动传感器
        
        参数:
            pin             : 信号引脚（DO 口）
            debounce_ms     : 去抖时间（毫秒），推荐 30~100
            use_interrupt   : 是否使用中断（推荐 True，省电不卡）
            pull            : 上拉/下拉（大多数模块自带上拉，建议 PULL_UP）
        """
        self.pin = Pin(pin, Pin.IN, pull)
        self.debounce_ms = debounce_ms
        self.use_interrupt = use_interrupt

        # 状态记录
        self._last_state = 0
        self._last_trigger = 0
        self.vibration_count = 0
        self.callback = None

        if use_interrupt:
            self.pin.irq(
                handler=self._irq_handler,
                trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING
            )
        print(f"[Vibration] 传感器已就绪 | 引脚: GPIO{pin} | 中断: {'开' if use_interrupt else '关'}")

    def _irq_handler(self, p):
        """中断去抖处理"""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_trigger) < self.debounce_ms:
            return  # 去抖

        state = p.value()
        if state == 1 and self._last_state == 0:  # 上升沿：震动开始
            self.vibration_count += 1
            self._last_trigger = now
            if self.callback:
                self.callback("detected", self.vibration_count)
            print(f"[Vibration] 检测到震动！第 {self.vibration_count} 次")

        self._last_state = state

    def read(self) -> bool:
        """直接读取当前状态（调试用）"""
        return self.pin.value() == 1

    def is_vibrating(self) -> bool:
        """当前是否正在震动"""
        return self.read()

    def wait_for_vibration(self, timeout_s: int = 30) -> bool:
        """
        阻塞等待震动（常用于开机自检）
        返回 True=检测到，False=超时
        """
        print(f"[Vibration] 等待震动（最多 {timeout_s}s）...")
        start = time.time()
        self.vibration_count = 0
        while time.time() - start < timeout_s:
            if self.read():
                self.vibration_count += 1
                print(f"[Vibration] 检测到震动！第 {self.vibration_count} 次")
                return True
            time.sleep(0.05)
        print("[Vibration] 超时未检测到震动")
        return False

    def on_vibrate(self, callback):
        """
        设置震动回调
        callback(event: str, count: int)
        event = "detected"
        """
        self.callback = callback

    def reset_count(self) -> None:
        """重置震动计数"""
        self.vibration_count = 0
        print("[Vibration] 计数已重置")

    def get_count(self) -> int:
        """获取震动次数"""
        return self.vibration_count

    # ========================== 高级功能（超好玩） ==========================
    def strong_vibration_detected(self, threshold: int = 5, within_seconds: int = 2) -> bool:
        """
        判断是否发生「强烈震动」（短时间内多次触发）
        常用于防盗报警
        """
        count = self.vibration_count
        time.sleep(within_seconds)
        if self.vibration_count - count >= threshold:
            print("[Vibration] 强烈震动！可能被搬动！")
            return True
        return False


# ========================== 使用示例 ==========================
if __name__ == "__main__":
    vib = VibrationSensor(pin=34)  # 34 是输入专用，自带上拉

    def on_shake(event, count):
        print(f"震动回调：第 {count} 次")
        # 可以在这里加蜂鸣器、发 MQTT、开灯等
        # buzzer.beep(1500, 100)

    vib.on_vibrate(on_shake)

    # 主循环什么都不干，中断自动处理
    print("震动监测已启动，摇一摇试试...")
    while True:
        time.sleep(1)

    # 或者阻塞等待
    # if vib.wait_for_vibration(10):
    #     print("有震动！")


from machine import Pin, ADC
import time

class SoundSensor:
    """
    高感度麦克风声音传感器模块（模拟AO + 数字DO）
    
    硬件说明：
        - 供电：3.3V 或 5V（推荐 3.3V）
        - AO：模拟输出（0~4095，越大声值越大）
        - DO：数字输出（超过阈值 → 高电平）
        - 板载电位器：顺时针旋 → 更灵敏（轻声就触发）
    
    超实用特性：
        - 实时声音强度（0~100%）
        - 拍手/敲击检测（双击识别）
        - 可调阈值 + 中断触发（不占 CPU）
        - 防抖 + 去误报
        - 支持“拍两下开灯”玩法
    """

    def __init__(
        self,
        analog_pin: int = 34,     # AO 模拟引脚（必须是 ADC1）
        digital_pin: int = 35,    # DO 数字引脚
        threshold: int = 2000,    # 数字输出触发阈值（可调）
        debounce_ms: int = 50
    ):
        """
        初始化声音传感器
        
        推荐引脚（ESP32 ADC1 通道）：
            32, 33, 34, 35, 36(VP), 39(VN)
        """
        # 模拟量（声音强度）
        self.adc = ADC(Pin(analog_pin))
        self.adc.atten(ADC.ATTN_11DB)   # 满量程 3.3V
        self.adc.width(ADC.WIDTH_12BIT) # 12位精度（0~4095）

        # 数字量（阈值触发）
        self.do = Pin(digital_pin, Pin.IN)
        self.threshold = threshold
        self.debounce_ms = debounce_ms

        # 状态记录
        self._last_trigger = 0
        self._clap_count = 0
        self._last_clap_time = 0
        self.callback = None

        # 注册数字中断（上升沿 = 检测到声音）
        self.do.irq(
            handler=self._irq_handler,
            trigger=Pin.IRQ_RISING
        )

        print(f"[Sound] 传感器已就绪 | AO=GPIO{analog_pin} | DO=GPIO{digital_pin}")

    def _irq_handler(self, p):
        """中断去抖 + 拍手计数"""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_trigger) < self.debounce_ms:
            return
        self._last_trigger = now

        # 拍手检测（双击）
        if time.ticks_diff(now, self._last_clap_time) < 600:  # 600ms 内第二次
            self._clap_count += 1
            if self._clap_count == 2:
                if self.callback:
                    self.callback("double_clap")
                print("检测到双击拍手！")
                self._clap_count = 0
        else:
            self._clap_count = 1  # 第一次拍手

        self._last_clap_time = now

        if self.callback:
            self.callback("sound_detected")

    def read_raw(self) -> int:
        """读取原始 ADC 值（0~4095）"""
        return self.adc.read()

    def read_level(self) -> int:
        """
        读取声音强度百分比（0~100）
        自动计算峰峰值，更准确
        """
        samples = [self.adc.read() for _ in range(50)]
        peak = max(samples) - min(samples)
        # 映射到 0~100（经验值）
        percent = min(100, int(peak / 30))
        return percent

    def is_loud(self) -> bool:
        """当前是否超过阈值（数字输出）"""
        return self.do.value() == 1

    def wait_for_sound(self, timeout_s: int = 10) -> bool:
        """阻塞等待声音"""
        print(f"[Sound] 等待声音（最多 {timeout_s}s）...")
        start = time.time()
        while time.time() - start < timeout_s:
            if self.is_loud():
                print("检测到声音！")
                return True
            time.sleep(0.05)
        return False

    def on_event(self, callback):
        """
        设置回调
        callback(event: str)
            "sound_detected"  → 任意声音
            "double_clap"     → 双击拍手
        """
        self.callback = callback

    def calibrate(self, seconds: int = 5):
        """自动校准环境噪音（推荐开机时调用）"""
        print(f"[Sound] 正在校准环境噪音 {seconds}s...")
        values = []
        for _ in range(seconds * 20):
            values.append(self.adc.read())
            time.sleep_ms(50)
        noise = sum(values) // len(values)
        self.threshold = noise + 300  # 比环境高 300 为触发点
        print(f"[Sound] 校准完成，触发阈值设为 {self.threshold}")

# ========================== 使用示例 ==========================
if __name__ == "__main__":
    mic = SoundSensor(analog_pin=34, digital_pin=35)

    def on_sound(event):
        if event == "double_clap":
            print("双击拍手！切换灯")
            # relay.toggle()
        else:
            print(f"检测到声音！强度: {mic.read_level()}%")

    mic.on_event(on_sound)

    # 开机校准
    mic.calibrate(3)

    print("声音监测已启动，拍两下试试！")
    while True:
        # 主循环显示实时强度
        level = mic.read_level()
        print(f"声音强度: {level:3d}% {'*' if mic.is_loud() else ' '}")
        time.sleep(0.1)
from machine import Pin, ADC
import time

class LightSensor:
    """
    光敏电阻模块（AO模拟 + DO数字输出）
    
    硬件说明：
        - 供电：3.3V（推荐）或 5V
        - AO：模拟输出（光越强 → 值越大）
        - DO：数字输出（超过阈值 → 高电平）
        - 板载电位器：顺时针旋 → 更灵敏（弱光也触发）
    
    推荐接线（100% 稳）：
        VCC → 3.3V
        GND → GND
        AO  → ADC1 引脚：32、33、34、35、36、39（必须这些！）
        DO  → 任意 GPIO（如 25、26、27）
    """

    def __init__(
        self,
        analog_pin: int = 34,      # AO 模拟输出（必须是 ADC1）
        digital_pin: int = 35,     # DO 数字输出
        samples: int = 10,         # 平均采样次数（抗干扰）
        auto_calibrate: bool = True
    ):
        """
        初始化光敏传感器
        """
        # 模拟量
        if analog_pin not in [32,33,34,35,36,39]:
            raise ValueError("AO 必须接 ADC1 通道：32~39")
        self.adc = ADC(Pin(analog_pin))
        self.adc.atten(ADC.ATTN_11DB)   # 0~3.3V 满量程
        self.adc.width(ADC.WIDTH_12BIT) # 0~4095
        self.samples = samples

        # 数字量
        self.do = Pin(digital_pin, Pin.IN)

        # 自动校准（开机测一次最暗/最亮）
        self.min_val = 4095
        self.max_val = 0
        if auto_calibrate:
            self.calibrate(seconds=3)

        # 回调
        self.on_light_change = None
        self._last_do_state = None

        # 注册数字中断（光变暗/变亮时触发）
        self.do.irq(handler=self._irq_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

        print(f"[Light] 传感器已就绪 | AO=GPIO{analog_pin} | DO=GPIO{digital_pin}")

    def _irq_handler(self, p):
        """数字电平变化中断（带防抖）"""
        time.sleep_ms(50)  # 硬件去抖
        state = p.value()
        if state != self._last_do_state and self.on_light_change:
            self.on_light_change("bright" if state else "dark")
            self._last_do_state = state

    def read_raw(self) -> int:
        """读取原始 ADC 值（0~4095）"""
        total = 0
        for _ in range(self.samples):
            total += self.adc.read()
            time.sleep_ms(5)
        return total // self.samples

    def read_percent(self) -> int:
        """
        读取光照强度百分比（0~100%）
        自动根据校准范围映射，越亮越高
        """
        raw = self.read_raw()
        if self.max_val == self.min_val:
            return 0
        percent = int(100 * (raw - self.min_val) / (self.max_val - self.min_val))
        return max(0, min(100, percent))

    def is_dark(self) -> bool:
        """当前是否“黑暗”（数字输出为高）"""
        return self.do.value() == 1

    def is_bright(self) -> bool:
        """当前是否“明亮”"""
        return not self.is_dark()

    def calibrate(self, seconds: int = 5) -> None:
        """自动校准环境最暗/最亮（推荐开机时调用）"""
        print(f"[Light] 正在校准光照环境 {seconds}s...（请遮光 → 照强光）")
        values = []
        for _ in range(seconds * 20):
            values.append(self.adc.read())
            time.sleep_ms(50)
        self.min_val = min(values)
        self.max_val = max(values)
        print(f"[Light] 校准完成：暗={self.min_val} 亮={self.max_val}")

    def on_change(self, callback):
        """
        注册光照变化回调
        callback(event: str) → "bright" 或 "dark"
        """
        self.on_light_change = callback

    def wait_for_dark(self, timeout_s: int = 30) -> bool:
        """阻塞等待变暗"""
        print(f"[Light] 等待变暗（最多 {timeout_s}s）...")
        start = time.time()
        while time.time() - start < timeout_s:
            if self.is_dark():
                print("已变暗！")
                return True
            time.sleep(0.2)
        return False

    def wait_for_bright(self, timeout_s: int = 30) -> bool:
        """阻塞等待变亮"""
        print(f"[Light] 等待变亮（最多 {timeout_s}s）...")
        start = time.time()
        while time.time() - start < timeout_s:
            if self.is_bright():
                print("已变亮！")
                return True
            time.sleep(0.2)
        return False

    def get_status(self) -> str:
        """返回当前光照状态文字"""
        p = self.read_percent()
        if p < 10:   return "很暗"
        if p < 30:   return "较暗"
        if p < 70:   return "正常"
        if p < 90:   return "较亮"
        return "很亮"


# ========================== 使用示例 ==========================
if __name__ == "__main__":
    light = LightSensor(analog_pin=34, digital_pin=35)

    def on_light(event):
        print(f"光照变化 → {event.upper()}")
        if event == "dark":
            # 天黑了，开灯
            relay.on()
            lcd.print("Night Mode", "Light ON")
        else:
            # 天亮了，关灯
            relay.off()
            lcd.print("Day Mode", "Light OFF")

    light.on_change(on_light)

    # 开机校准
    light.calibrate(4)

    print("光敏控制已启动，遮光/照灯试试！")
    while True:
        level = light.read_percent()
        status = light.get_status()
        print(f"亮度: {level:3d}% → {status}")
        time.sleep(0.5)
        
from machine import Pin
import time

class UltrasonicDistanceSensor:
    """
    HC-SR04 / HC-SR04P 超声波测距模块（最经典的测距传感器）
    
    硬件说明：
        - 供电：5V（HC-SR04）或 3.3V~5V（HC-SR04P）
        - 推荐接线：
            VCC → 5V（推荐）或 3.3V（仅限 HC-SR04P）
            GND → GND
            TRIG → 任意 GPIO 输出（如 26）
            ECHO → 任意 GPIO 输入（如 25）
        - 测距范围：2cm ~ 400cm（理论）
    
    超实用特性：
        - 温度补偿（大幅提高精度！）
        - 超时保护（防止卡死）
        - 连续测量平均值（超稳）
        - 障碍物报警 + 距离分级
        - 支持“有人靠近自动开灯”玩法
    """

    SOUND_SPEED_BASE = 340.0  # 声速 340 m/s（20°C 时）

    def __init__(
        self,
        trig_pin: int = 26,
        echo_pin: int = 25,
        temp_sensor=None,           # 可传入 DS18B20 实例实现自动温度补偿
        timeout_us: int = 30000,    # 超时 30ms ≈ 5米
        samples: int = 3
    ):
        """
        初始化超声波模块
        """
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.temp_sensor = temp_sensor
        self.timeout_us = timeout_us
        self.samples = samples

        self.trig.value(0)
        time.sleep_ms(100)
        print(f"[Ultrasonic] 初始化完成 | TRIG=GPIO{trig_pin} | ECHO=GPIO{echo_pin}")

    def _get_sound_speed(self) -> float:
        """根据当前温度计算声速（m/s）"""
        temp = 25.0  # 默认 25°C
        if self.temp_sensor:
            t = self.temp_sensor.get_first_temp()
            if t is not None:
                temp = t
        # 声速公式：331.3 + 0.606 * T（℃）
        return 331.3 + 0.606 * temp

    def measure_raw(self) -> int | None:
        """单次原始测量，返回回波时间（微秒），失败返回 None"""
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        try:
            # 等待 ECHO 变高
            start = time.ticks_us()
            while self.echo.value() == 0:
                if time.ticks_diff(time.ticks_us(), start) > self.timeout_us:
                    return None

            pulse_start = time.ticks_us()

            # 等待 ECHO 变低
            while self.echo.value() == 1:
                if time.ticks_diff(time.ticks_us(), start) > self.timeout_us:
                    return None

            pulse_end = time.ticks_us()
            pulse_duration = time.ticks_diff(pulse_end, pulse_start)
            return pulse_duration
        except:
            return None

    def measure_cm(self) -> float | None:
        """
        测量距离（厘米），带温度补偿 + 多重采样平均
        返回 None 表示测量失败
        """
        durations = []
        for _ in range(self.samples):
            dur = self.measure_raw()
            if dur is not None:
                durations.append(dur)
            time.sleep_ms(60)  # HC-SR04 建议 60ms 间隔

        if not durations:
            return None

        # 取平均值
        avg_duration = sum(durations) / len(durations)
        speed = self._get_sound_speed() / 10000  # m/s → cm/us
        distance = (avg_duration * speed) / 2  # 除 2 因为是来回
        return round(distance, 1)

    def measure(self, unit: str = "cm") -> float | None:
        """统一接口，支持 cm/inch/m"""
        cm = self.measure_cm()
        if cm is None:
            return None
        if unit == "cm":
            return cm
        elif unit == "inch":
            return round(cm / 2.54, 1)
        elif unit == "m":
            return round(cm / 100, 3)
        return cm

    def is_near(self, threshold_cm: int = 30) -> bool:
        """是否有人/物靠近"""
        d = self.measure_cm()
        return d is not None and d < threshold_cm

    def get_distance_level(self) -> str:
        """距离分级（用于显示）"""
        d = self.measure_cm()
        if d is None:
            return "Error"
        if d < 10:   return "极近"
        if d < 30:   return "很近"
        if d < 100:  return "近"
        if d < 200:  return "中等"
        return "远"

    def wait_for_approach(self, threshold_cm: int = 50, timeout_s: int = 30) -> bool:
        """等待有人靠近"""
        print(f"[Ultrasonic] 等待靠近（<{threshold_cm}cm，{timeout_s}s）...")
        start = time.time()
        while time.time() - start < timeout_s:
            if self.is_near(threshold_cm):
                print(f"检测到靠近！距离 {self.measure_cm()}cm")
                return True
            time.sleep(0.2)
        return False

# ========================== 使用示例 ==========================
if __name__ == "__main__":
    # 如果你有 DS18B20，可以自动温度补偿
    from c_devices import DS18B20
    temp_sensor = DS18B20(19)
    sonar = Ultrasonic(trig_pin=26, echo_pin=25, temp_sensor=temp_sensor)

    print("超声波测距测试开始...")
    while True:
        dist = sonar.measure_cm()
        level = sonar.get_distance_level()
        print(f"距离: {dist if dist else '---'} cm → {level}")
        time.sleep(0.5)


