from c_utils import FileUtil,WiFiUtil
import network
import socket
import camera
import time
import gc

WIFI_SSID = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# 设置服务器地址和端口
SERVER_IP = '192.168.2.101'
SERVER_PORT = 8080
CAMERA_INIT_FLAG = False
class Webcam:
    def __init__(self, wifi_ssid, wifi_password):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.server_socket = None
        self.client_socket = None
        

    def _init_wifi(self):
        # 初始化WiFi
        wifi = WiFiUtil()
        wifi.do_connect(WIFI_SSID, WIFI_PASSWORD)

    # 启动摄像头服务器
    def start_server(self):
        self._init_wifi()
        # 创建服务器套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', SERVER_PORT))
        self.server_socket.listen(1)
        print('Server started. Listening on port', SERVER_PORT)


    def capture_and_send(self, client_socket):
        global CAMERA_INIT_FLAG

        if not CAMERA_INIT_FLAG:
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

        CAMERA_INIT_FLAG = True
        try:
            while True:
                # 捕获图像并发送给客户端
                print('Capturing and sending image...')
                img = camera.capture()
                #img_size = len(img)
                #print('img_size: ', img_size)
                # 构建HTTP响应头
                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: %s\r\n\r\n' % str(len(img))
                # 发送响应头
                client_socket.send(response_header.encode())

                # 发送图像数据
                client_socket.send(img)
                time.sleep(0.1)
        except Exception as e:
            print('Exception:', e)
            camera.deinit()
            camera.init(0, format=camera.JPEG)
            client_socket.close()
        finally:
            pass
            #client_socket.close()

        # 执行垃圾回收以释放内存
        # gc.collect()

    def handle_client(self, client_socket):
        request = client_socket.recv(1024)
        if request:
            print('Received request:', request)
            self.capture_and_send(client_socket)
        # 关闭客户端连接
        client_socket.close()


    def run(self):
        self.start_server()

        while True:
            try:
                 # 等待客户端连接
                print('Waiting for client connection...')
                client_socket, client_addr = self.server_socket.accept()
                print('Client connected:', client_addr)
                print('Client connected:', client_socket)
                self.handle_client(client_socket)
            except Exception as e:
                print('Exception:', e)
                break
            finally:
                camera.deinit()

        self.server_socket.close()

def main():
    webcam = Webcam(WIFI_SSID,WIFI_PASSWORD)
    webcam.run()


if __name__ == '__main__':
    main()
