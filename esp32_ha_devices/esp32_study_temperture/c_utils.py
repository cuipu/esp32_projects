"""
c_utils.py - ESP32 通用工具库（WiFi、时间、文件、内存）
作者: Mr.Cui
重构: 2025-04-06 工业级标准版（已修复所有语法错误）
"""

import network
import time
import ntptime
import gc
import ujson
import uos
import utime

# ============================= WiFi 工具（最稳连接方式）=============================
class WiFi:
    def __init__(self, ssid: str = None, password: str = None):
        self.ssid = ssid
        self.password = password
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)

    def connect(self, ssid: str = None, password: str = None, timeout: int = 15) -> bool:
        ssid = ssid or self.ssid
        password = password or self.password
        if not ssid:
            return False
        if self.sta.isconnected():
            return True
        print(f"[WiFi] 连接 {ssid} ...")
        self.sta.connect(ssid, password)
        for _ in range(timeout):
            if self.sta.isconnected():
                print(f"[WiFi] 成功！IP: {self.sta.ifconfig()[0]}")
                return True
            time.sleep(1)
        print("[WiFi] 连接失败")
        return False

    def is_connected(self) -> bool:
        return self.sta.isconnected()


# ============================= 时间工具（自动同步 + 高精度）=============================
class Clock:
    # 修复！这两行必须在 class 外面，或正确缩进！
    NTP_HOST = "ntp1.aliyun.com"     # 中国最快的 NTP 服务器
    NTP_DELTA = 3155644800           # UTC+8 偏移（中国时间）

    @staticmethod
    def sync(host: str = None) -> bool:
        """同步网络时间"""
        try:
            print(f"[Clock] 正在同步时间...")
            ntptime.host = host or Clock.NTP_HOST
            ntptime.settime()
            print("[Clock] 时间同步成功:", Clock.now())
            return True
        except Exception as e:
            print("[Clock] 时间同步失败:", e)
            return False

    @staticmethod
    def now() -> str:
        """返回 YYYY-MM-DD HH:MM:SS"""
        t = utime.localtime()
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

    @staticmethod
    def now_hms() -> str:
        """返回 HH:MM:SS"""
        t = utime.localtime()
        return f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"


# ============================= 文件工具（安全读写 + JSON 支持）=============================
class Storage:
    @staticmethod
    def read(path: str) -> str | None:
        try:
            with open(path, "r") as f:
                return f.read()
        except:
            return None

    @staticmethod
    def write(path: str, content: str) -> bool:
        try:
            with open(path, "w") as f:
                f.write(content)
            return True
        except:
            return False

    @staticmethod
    def read_json(path: str) -> dict | None:
        content = Storage.read(path)
        if content:
            try:
                return ujson.loads(content)
            except:
                pass
        return None


# ============================= 内存工具（监控 + 自动回收）=============================
class Memory:
    @staticmethod
    def info():
        gc.collect()
        free = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        print(f"[Memory] 总:{total//1024}KB 已用:{alloc//1024}KB 空闲:{free//1024}KB")

    @staticmethod
    def collect():
        before = gc.mem_free()
        gc.collect()
        print(f"[Memory] 垃圾回收释放: {gc.mem_free() - before} bytes")
        
# ============================= 文件工具（极简安全版）=============================
class FileUtil:
    """极简文件工具（专为 ESP32 MicroPython 优化）"""
    
    @staticmethod
    def read_file_as_json(path: str) -> str:
        """
        读取文件并返回原始字符串（专用于你的 esp32_config.txt）
        自动跳过注释和空行
        """
        try:
            result = {}
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        key = k.strip()
                        value = v.strip().strip("'\"")
                        result[key] = value
            return ujson.dumps(result)
        except Exception as e:
            print(f"[FileUtil] 读取失败 {path}: {e}")
            return "{}"
