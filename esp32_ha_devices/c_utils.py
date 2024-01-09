'''
Author: cuipu g050505@gmail.com
Date: 2023-04-26 13:10:52
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2024-01-09 22:05:50
FilePath: \esp32_projects\esp32_ha_devices\c_utils.py
Description: ESP32 WiFi小工具

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''

import _thread
import re
import utime
import uos
import os
import network
import time
import ujson
import gc
import usocket
import ntptime
from machine import Timer

#import ulogging as logging
#logging.basicConfig(level=logging.INFO)
#log = logging.getLogger('app')

"""
扫描当前可以连接的无线网络。
只能在 STA 模式下进行扫描，使用元组列表的形式返回 WiFi 接入点的相关信息。
（ssid, bssid, channel, rssi, authmode, hidden）
"""
class WiFiUtil:

    '''
    description: 初始化
    param {*} self
    param {*} wifi_ssid WiFi名称
    param {*} wifi_password WiFi密码 
    return {*}
    '''

    def __init__(self):
        self.wifi_ssid = ''
        self.wifi_password = ''
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wifi_config = None
        self.wifi_is_connected = False

    def do_connect(self, wifi_ssid: str, wifi_password: str,timeout=15):
        '''
        连接网络，添加超时逻辑
        '''
        start_time = utime.time()
        try:
            self.wifi_ssid = wifi_ssid
            self.wifi_password = wifi_password
            if not self.wlan.isconnected():
                print("Connecting to WiFi...")
                self.wlan.connect(wifi_ssid, wifi_password)
                while not self.wlan.isconnected() and utime.time() - start_time < timeout:
                    print("connecting...{}".format(i))
                    time.sleep(1)
                if self.wlan.isconnected():
                    print("Connected to WiFi")
                    self.wifi_is_connected = True
                    self.wifi_config = self.wlan.ifconfig()
                    self.show_current_wifi_config()
                else:
                    print("Failed to connect to WiFi within the specified timeout")

        except MemoryError:
            print("Memory error occurred. Restarting...")
        except OSError as e:
            error_code = e.args[0]
            error_name = uerrno.errorcode[error_code]
            print("OSError:", error_name)
        except Exception as e:
            print(f"Exception occurred: {e}")
            # sys.print_exception(e) 
        

    def is_connected(self):
        '''
        判断是否连接网络
        '''
        return self.wlan.isconnected()

    def get_current_wifi_config(self):
        '''
        description: 显示当前连接的WiFi信息
        return {*}
        '''
        if not self.wlan.isconnected():
            self.do_connect(wifi_ssid, wifi_password)
            self.wifi_config = self.wlan.ifconfig()
        else:
            self.wifi_config = self.wlan.ifconfig()

        return self.wifi_config

    def show_current_wifi_config(self):
        if not self.wlan.isconnected():
            self.do_connect(wifi_ssid, wifi_password)
            self.wifi_config = self.wlan.ifconfig()
            print("WiFi config is\n ip: {} \n subnet mask: {}\n gateway:{}\n broadcast address: {}\n".format(
                self.wifi_config[0], self.wifi_config[1], self.wifi_config[2], self.wifi_config[3]))
        else:
            print("WiFi config is\n ip: {} \n subnet mask: {}\n gateway:{}\n broadcast address: {}\n".format(
                self.wifi_config[0], self.wifi_config[1], self.wifi_config[2], self.wifi_config[3]))



    def get_wifi_information_list(self):
        '''
        description: 获取当前WiFi 详细信息列表
        return {*}
        '''
        # eg: [b'TP-LINK_502_2.4G', b'ChinaNet-IaEh', b'TP-LINK_1DE0', b'TP-LINK_397D', b'CU-101', b'', b'CU_43Lc', b'@PHICOMM_98', b'201', b'102', b'TP-LINK_7252', b'501', b'602', b'Tenda88898', b'HONOR-510MM1']
        return self.wlan.scan()


    def show_wifi_ssid_list(self):
        '''
        description: 获取当前WiFi名称列表
        return {*}
        '''
        wifi_information_list = self.wlan.scan()
        wifi_ssid_list = []
        wifi_ssid = ''
        for wifi_information in wifi_information_list:
            # eg:b'TP-LINK_502_2.4G'，需要将byte转为str
            wifi_ssid = wifi_information[0]
            wifi_ssid_list.append(str(wifi_ssid, 'utf-8'))
        # print('wifi_ssid_list {}'.format(wifi_ssid_list))
        return wifi_ssid_list



class FileUtil:
    """
    文件操作工具类。
    """

    def __init__(self):
        pass

    @staticmethod
    def create_directory(path):
        """
        创建目录。

        参数：
            path: 目录路径。
        """
        try:
            uos.mkdir(path)
        except OSError as e:
            if e.args[0] != uos.EEXIST:
                print("创建目录失败: {}".format(e))

    @staticmethod
    def read_file(filename):
        """
        读取文件内容。

        参数：
            filename: 文件名。

        返回值：
            文件内容。
        """
        try:
            with open(filename, 'r') as f:
                return f.read()
        except OSError as e:
            print("读取文件失败: {}".format(e))

    @staticmethod
    def write_file(filename, content):
        """
        写入文件内容。

        参数：
            filename: 文件名。
            content: 文件内容。
        """
        try:
            with open(filename, 'w') as f:
                f.write(content)
        except OSError as e:
            print("写入文件失败: {}".format(e))
    
    def write_file_by_byte(filename, content):
        """
        写入文件内容。

        参数：
            filename: 文件名。
            content: 文件内容。
        """
        try:
            with open(filename, 'wb') as f:
                f.write(content)
        except OSError as e:
            print("写入文件失败: {}".format(e))

    @staticmethod
    def append_file(filename, content):
        """
        追加文件内容。

        参数：
            filename: 文件名。
            content: 追加内容。
        """
        try:
            with open(filename, 'a') as f:
                f.write(content)
        except OSError as e:
            print("追加文件失败: {}".format(e))

    @staticmethod
    def rename_file(old_filename, new_filename):
        """
        重命名文件。

        参数：
            old_filename: 旧文件名。
            new_filename: 新文件名。
        """
        try:
            uos.rename(old_filename, new_filename)
        except OSError as e:
            print("重命名文件失败: {}".format(e))

    @staticmethod
    def delete_file(filename):
        """
        删除文件。

        参数：
            filename: 文件名。
        """
        try:
            uos.remove(filename)
        except OSError as e:
            print("删除文件失败: {}".format(e))

    @staticmethod
    def recursive_dirs(root, filter_func=None):
        """
        TODO 不能用
        递归获取目录列表。

        参数：
            root: 要递归的根目录。
            filter_func: 过滤函数，用于过滤目录列表，默认为 None，即不过滤。

        返回值：
            包含目录路径的列表。
        """
        dirs = []
        try:
            for dirpath, dirnames, _ in os.walk(root):
                for dirname in dirnames:
                    dirpath = os.path.join(dirpath, dirname)
                    if filter_func is None or filter_func(dirpath):
                        dirs.append(dirpath)
        except OSError as e:
            print("递归获取目录列表失败: {}".format(e))

        return dirs

    @staticmethod
    def recursive_files(root, filter_func=None, sort_func=None, reverse=True):
        """
        TODO 不能用
        递归获取文件列表。

        参数：
            root: 要递归的根目录。
            filter_func: 过滤函数，用于过滤文件列表，默认为 None，即不过滤。
            sort_func: 排序函数，用于排序文件列表，默认为按创建时间排序。
            reverse: 是否倒序排列，默认为 True。

        返回值：
            包含文件路径的列表。
        """
        files = []
        try:
            for dirpath, _, filenames in os.walk(root):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if filter_func is None or filter_func(filepath):
                        files.append(filepath)
        except OSError as e:
            print("递归获取文件列表失败: {}".format(e))

        if sort_func is None:
            def sort_func(x): return utime.gmtime(
                os.stat(x).st_ctime)  # 按创建时间排序

        files.sort(key=sort_func, reverse=reverse)
        return files

    @staticmethod
    def read_file_as_json(file_path):
        """
        读取文件中的键值对，并将其转换为 JSON 格式

        参数：
            file_path: 文件路径

        返回值：
            包含键值对的 JSON 对象
        """
        result = {}
        in_comment_block = False

        try:
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if not line or line.startswith("#") or in_comment_block:
                        continue
                    # 使用正则表达式匹配键值对
                    match = re.match(r'^(\w+)\s*=\s*(.*)$', line)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        result[key] = value
                    elif line.startswith("'''"):
                        in_comment_block = True
                    elif line.endswith("'''"):
                        in_comment_block = False

        except OSError as e:
            print("读取文件失败: {}".format(e))

        # 使用 ujson 将字典转换为 JSON 格式
        return ujson.dumps(result)


class MultiThreadUtil:
    """
    多线程工具类，用于封装多线程操作相关方法
    """

    @staticmethod
    def start_new_thread(function, args=()):
        """
        开启一个新线程

        :param function: 线程要执行的函数
        :type function: function
        :param args: 线程要执行的函数的参数，为元组类型，默认为空元组
        :type args: tuple, optional
        """
        try:
            thread_id = _thread.start_new_thread(function, args)
        except:
            print("Error: 无法启动线程")
        return thread_id
        

    @staticmethod
    def allocate_lock():
        """
        分配并返回一个新的锁

        :return: 返回一个新的锁对象
        :rtype: lock object
        """
        return _thread.allocate_lock()

    @staticmethod
    def exit():
        """
        终止当前线程

        """
        try:
            _thread.exit()
        except:
            print("Error: 无法终止线程")

    def try_except(self, try_func, except_func=None):
        """
        尝试执行一个函数并捕捉其异常。如果出现异常，则执行指定的异常处理函数。

        参数:
        try_func (function): 要尝试执行的函数。
        except_func (function): 异常处理函数。默认为空。
        """
        try:
            try_func()
        except Exception as e:
            if except_func:
                except_func(e)

    def try_finally(self, try_func, finally_func=None):
        """
        尝试执行一个函数并在结束后执行指定的结束函数。

        参数:
        try_func (function): 要尝试执行的函数。
        finally_func (function): 结束函数。默认为空。
        """
        try:
            try_func()
        finally:
            if finally_func:
                finally_func()

 
class MemoryUtil:
    def __init__(self):
        self.start_free = 0
        self.start_alloc = 0
    
    def measure_memory(self):
        """
        检测当前的内存使用情况
        """
        gc.collect()
        self.start_free = gc.mem_free()
        self.start_alloc = gc.mem_alloc()
        print("Free memory: {} bytes".format(self.start_free))
        print("Allocated memory: {} bytes".format(self.start_alloc))
    
    def find_largest_objects(self, num_objects):
        """
        查找并打印占用内存最大的对象
        """
        objs = gc.get_objects()
        objs.sort(key=lambda obj: -sys.getsizeof(obj))
        print("Top {} largest objects:".format(num_objects))
        for i in range(num_objects):
            obj = objs[i]
            size = sys.getsizeof(obj)
            print("Object {}: size={} bytes".format(i + 1, size))
    
    def collect_garbage(self):
        """
        执行垃圾回收，释放不再使用的内存
        """
        gc.collect()
        print("Garbage collection completed.")
    
    def memory_diff(self):
        """
        检测内存变化情况
        """
        end_free = gc.mem_free()
        end_alloc = gc.mem_alloc()
        diff_free = end_free - self.start_free
        diff_alloc = end_alloc - self.start_alloc
        print("Memory difference:")
        print("Free memory: {} bytes".format(diff_free))
        print("Allocated memory: {} bytes".format(diff_alloc))

    

class TimeUtil:

   
    def format_datetime(self, timestamp):
        """
        格式化时间戳为"yyyy-MM-dd HH:mm:ss"格式的字符串

        参数:
        - timestamp: 时间戳

        返回值:
        - 格式化后的时间字符串
        """
        year, month, day, hour, minute, second, _, _ = utime.localtime(timestamp)
        formatted_datetime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            year, month, day, hour, minute, second
        )
        return formatted_datetime
    
    def format_datetime_hms(self, timestamp):
        """
        格式化时间戳为"HH:mm:ss"格式的字符串

        参数:
        - timestamp: 时间戳

        返回值:
        - 格式化后的时间字符串
        """
        year, month, day, hour, minute, second, _, _ = utime.localtime(timestamp)
        formatted_datetime = "{:02d}:{:02d}:{:02d}".format(
            hour, minute, second
        )
        return formatted_datetime

   
    def get_current_timestamp(self):
        """
        获取当前时间戳

        返回值:
        - 当前时间戳
        """
        return utime.time()

    
    def get_current_datetime(self):
        """
        获取当前时间的格式化字符串"yyyy-MM-dd HH:mm:ss"

        返回值:
        - 当前时间的格式化字符串
        """
        current_timestamp = self.get_current_timestamp()
        current_datetime = self.format_datetime(current_timestamp)
        return current_datetime

    def get_current_datetime_hms(self):
        """
        获取当前时间的格式化字符串"HH:mm:ss"

        返回值:
        - 当前时间的格式化字符串
        """
        current_timestamp = self.get_current_timestamp()
        current_datetime = self.format_datetime_hms(current_timestamp)
        return current_datetime

    def synchronised_local_time(self):
        """
        同步本地时间，需要先联网
        """
        ntptime.NTP_DELTA = 3155644800  # 可选 UTC+8偏移时间（秒），不设置就是UTC0
        ntptime.host = 'ntp1.aliyun.com'  # 可选，ntp服务器，默认是"pool.ntp.org" 这里使用阿里服务器
        ntptime.settime()  # 修改设备时间,到这就已经设置好了
        return self.get_current_datetime()

    def synchronised_time_every_seven_hours(self):
        """
        定时任务:每个7小时重新同步一次时间
        """
        timer = Timer(1)
        timer.init(period=1000 * 60 * 60 * 7, mode=Timer.PERIODIC, callback=sync_ntp)
        
def time_util_test():
    time_util = TimeUtil()

    # 格式化时间戳
    timestamp = 1621538400
    formatted_time = time_util.format_datetime(timestamp)
    print("Formatted Time:", formatted_time)

    # 获取当前时间戳
    current_timestamp = time_util.get_current_timestamp()
    print("Current Timestamp:", current_timestamp)

    # 格式化当前时间
    current_datetime = time_util.get_current_datetime()
    print("Current Datetime:", current_datetime)




class DNSResolver:
    def __init__(self):
        self.sock = None

    def connect(self, host, port=80):
        try:
            addr = usocket.getaddrinfo(host, port)[0][-1]
            self.sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
            self.sock.connect(addr)
        except Exception as e:
            print("Connection error:", e)

    def send_request(self, request):
        try:
            self.sock.send(request)
        except Exception as e:
            print("Send request error:", e)

    def receive_response(self, buffer_size=4096):
        try:
            return self.sock.recv(buffer_size)
        except Exception as e:
            print("Receive response error:", e)

    def close(self):
        try:
            self.sock.close()
        except Exception as e:
            print("Close socket error:", e)

    @staticmethod
    def get_public_ip(domain):
        try:
            addr_info = usocket.getaddrinfo(domain, 80)
            if len(addr_info) > 0:
                ip = addr_info[0][-1][0]
                return ip
            else:
                print("Failed to retrieve IP address for domain:", domain)
                return None
        except Exception as e:
            print("Error retrieving public IP:", e)
            return None


# WiFi配置
WIFI_SSID = 'AX6K'
WIFI_PASSWORD = '1234567890...'
def test():
    wifi = WiFiUtil()
    wifi.do_connect(WIFI_SSID, WIFI_PASSWORD)
    domain = 'www.cuipu.net'
    public_ip = DNSResolver.get_public_ip(domain)
    if public_ip:
        print("Public IP for domain '{0}': {1}".format(domain, public_ip))
    else:
        print("Failed to retrieve the public IP for domain '{0}'".format(domain))
    time_util = TimeUtil()
    time_util.synchronised_local_time()
    current_timestamp = time_util.get_current_timestamp()
    print("current_timestamp: " + time_util.format_datetime(current_timestamp))


def main():
    test()


if __name__ == "__main__":
    main()