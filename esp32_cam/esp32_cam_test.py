'''
Author: cuipu g050505@gmail.com
Date: 2023-05-19 23:01:38
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-20 10:49:40
FilePath: \esp32_projects\esp32_cam\esp32_cam_test.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import socket
import network
import camera
import time

class ESP32Cam:
    def __init__(self):
    
        self.led =  Pin(4, Pin.OUT)
        self._init_wifi()
    
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
                time.sleep(0.1)
        except:
            pass
        finally:
            camera.deinit()

def camera_test():


    # 初始化摄像头
    try:
        camera.init(0, format=camera.JPEG)
    except Exception as e:
        camera.deinit()
        camera.init(0, format=camera.JPEG)

    # 拍摄一张图片
    buf = camera.capture()  # 大小是640x480

    # 保存图片到文件
    with open("第一张图片.png", "wb") as f:
        f.write(buf)  # buf中的数据就是图片的数据，所以直接写入到文件就行了
        print("拍照已完成，点击Thonny左侧【MicroPython设备】右侧的三，\n然后看到‘刷新’，点击刷新会看到 图片，\n然后右击图片名称，选择下载到电脑的路径即可...")

    camera.deinit()



def main():
    
    camera_test()


if __name__ == "__main__":
    main()