'''
Author: cuipu g050505@gmail.com
Date: 2023-04-29 22:23:22
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2025-12-17 18:34:02
FilePath: \esp32_projects\esp32_ha_devices\esp32_study_temperture\c_device.py
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

        # 设置所有探头精度
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
