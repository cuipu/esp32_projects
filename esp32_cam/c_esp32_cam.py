'''
Author: cuipu g050505@gmail.com
Date: 2023-05-11 22:03:16
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-21 01:16:43
FilePath: \esp32_projects\esp32_cam\c_esp32_cam.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import camera
from c_utils import WiFiUtil, TimeUtil,FileUtil
import socket
import uos
import utime
import ustruct
import os
from machine import SDCard,Pin, disable_irq, enable_irq
import machine

WIFI_SSID = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'
SDCARD_DIR = '/sd'
class ESP32Cam:
    def __init__(self):
        
        self.led = Pin(4, Pin.OUT)
        self._init_wifi()
        # 挂载SD卡
        self.mount_sdcard()
        self.file_util = FileUtil()
        self.time_util = TimeUtil()
    
    def is_sdcard_mounted(self):
        try:
            uos.listdir(SDCARD_DIR)
            return True
        except OSError:
            return False

    def mount_sdcard(self,sdcard_dir = SDCARD_DIR):
        try:
            if self.is_sdcard_mounted():
                print("sdcard is mounted")
            else:
                uos.mount(SDCard(), sdcard_dir)
        except Exception as ret:
            print("mount failed...", ret)
        else:
            print("mount succeed...")

    def flash_led(self):
        self.led.value(1)
        utime.sleep(1)
        self.led.value(0)

    def take_photo(self, photo_dir = SDCARD_DIR):

        # 初始化摄像头 TODO 照相这里有问题
        try:
            photo_path = photo_dir + '/' + str(utime.ticks_us()) + '.png'

            camera.init(0, format=camera.JPEG)
            # 拍摄一张图片
            buf = camera.capture()  # 大小是640x480
           
            self.file_util.write_file_by_byte(photo_path,buf)
            # 保存图片到文件

            #self.led.value(0)
        except Exception as e:
            camera.deinit()
            camera.init(0, format=camera.JPEG)
        finally:
            camera.deinit()

    def _init_wifi(self):
        # 初始化WiFi
        wifi = WiFiUtil()
        wifi.do_connect(WIFI_SSID, WIFI_PASSWORD)


    def send_camera_feed(self,server_ip : str,server_port:int):
        # 摄像头初始化
        try:
            camera.init(0, format=camera.JPEG)
        except Exception as e:
            camera.deinit()
            camera.init(0, format=camera.JPEG)
        
        # 其他设置：
        # 上翻下翻
        camera.flip(0)
        #左/右
        camera.mirror(1)

        # 分辨率
        camera.framesize(camera.FRAME_HVGA)
        # 选项如下：
        # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
        # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
        # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
        # FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
        # FRAME_P_FHD FRAME_QSXGA
        # 有关详细信息，请查看此链接：https://bit.ly/2YOzizz

        # 特效
        camera.speffect(camera.EFFECT_NONE)
        #选项如下：
        # 效果\无（默认）效果\负效果\ BW效果\红色效果\绿色效果\蓝色效果\复古效果
        # EFFECT_NONE (default) EFFECT_NEG \EFFECT_BW\ EFFECT_RED\ EFFECT_GREEN\ EFFECT_BLUE\ EFFECT_RETRO

        # 白平衡
        # camera.whitebalance(camera.WB_HOME)
        #选项如下：
        # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

        # 饱和
        camera.saturation(0)
        #-2,2（默认为0）. -2灰度
        # -2,2 (default 0). -2 grayscale 

        # 亮度
        camera.brightness(0)
        #-2,2（默认为0）. 2亮度
        # -2,2 (default 0). 2 brightness

        # 对比度
        camera.contrast(0)
        #-2,2（默认为0）.2高对比度
        #-2,2 (default 0). 2 highcontrast
        
        # 质量
        camera.quality(10)
        #10-63数字越小质量越高
        # socket UDP 的创建
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)

        try:
            while True:
                buf = camera.capture()  # 获取图像数据
                s.sendto(buf, (server_ip, server_port))  # 向服务器发送图像数据
                utime.sleep(0.1)
        except Exception as e:
            print('Exception:', e)
            camera.deinit()
            camera.init(0, format=camera.JPEG)
        finally:
            camera.deinit()

    
def main():
    
    esp32_cam = ESP32Cam()
    esp32_cam.send_camera_feed('192.168.2.10',9090)



if __name__ == "__main__":
    main()