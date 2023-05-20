'''
Author: cuipu g050505@gmail.com
Date: 2023-05-20 10:16:03
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-20 22:08:50
FilePath: \esp32_projects\esp32_cam\webcam02.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
WIFI_SSID = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# 设置服务器地址和端口
SERVER_IP = '0.0.0.0'
SERVER_PORT = 9090

import network
import usocket as socket
import uerrno
import uos
import gc
from machine import Pin
import camera

CAMERA_INIT_FLAG = False

class Webcam:
    def __init__(self, ssid, password, port=8080):
        self.ssid = ssid
        self.password = password
        self.port = port
        self.server_socket = None
        self.client_socket = None

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('Connecting to WiFi...')
            wlan.connect(self.ssid, self.password)
            while not wlan.isconnected():
                pass
        print('WiFi connected:', wlan.ifconfig())

    def start_server(self):
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]

        self.server_socket = socket.socket()
        self.server_socket.bind(addr)
        self.server_socket.listen(1)

        print('Server started. Waiting for connections...')

        while True:
            try:
                self.client_socket, _ = self.server_socket.accept()
                print('Client connected')

                request = self.client_socket.recv(1024)
                request = str(request, 'utf-8')

                if request.startswith('GET /'):
                    self.send_image()
                else:
                    self.send_response(404, 'Not Found')

            except OSError as e:
                if e.args[0] == uerrno.ECONNRESET:
                    print('Connection reset by peer')
                else:
                    print('Socket error:', e)
                self.close_client()

            except Exception as e:
                print('Error:', e)
                self.close_client()

    def send_response(self, status_code, status_text, content_type='text/plain', content=''):
        response = 'HTTP/1.1 {} {}\r\n'.format(status_code, status_text)
        response += 'Content-Type: {}\r\n'.format(content_type)
        response += 'Content-Length: {}\r\n'.format(len(content))
        response += '\r\n'
        response += content

        self.client_socket.sendall(response.encode('utf-8'))
        # self.close_client()


    def send_image(self):
        global CAMERA_INIT_FLAG

        try:
            if not CAMERA_INIT_FLAG:
                    # 摄像头初始化
                try:
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
                except Exception as e:
                    camera.deinit()
                    camera.init(0, format=camera.JPEG)
            image = camera.capture()
            content_type = 'image/jpeg'
            self.send_response(200, 'OK', content_type, str(image))
        except Exception as e:
            camera.deinit()
            camera.init(0, format=camera.JPEG)
            print('Failed to capture image:', e)
            self.send_response(500, 'Internal Server Error')

    def close_client(self):
        if self.client_socket is not None:
            self.client_socket.close()
            self.client_socket = None
            print('Client disconnected')

    def close_server(self):
        self.close_client()
        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None
            print('Server stopped')



def main():
    # 设置 WiFi SSID 和密码
    ssid = 'YourWiFiSSID'
    password = 'YourWiFiPassword'

    # 创建 Webcam 实例
    webcam = Webcam(WIFI_SSID, WIFI_PASSWORD)

    # 连接 WiFi
    webcam.connect_wifi()

    # 启动服务器
    webcam.start_server()

# 运行主函数
if __name__ == '__main__':
    main()