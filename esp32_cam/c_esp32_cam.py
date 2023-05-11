import camera
from c_utils import FileUtil,WiFiUtils
import socket

WIFI_SSID = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

class ESP32Cam:
    def __init__(self):
        self.camera.init(0, format=camera.JPEG)

    def take_photo(self, photo_dir = None, photo_name = None):
        # 初始化摄像头
        try:
            
                # 拍摄一张图片
            buf = self.camera.capture()  # 大小是640x480

            self.photo_path = photo_dir + photo_name

            FileUtil().write_file_by_binary(photo_path, buf)
        except Exception as e:
            self.camera.deinit()
            self.camera.init(0, format=camera.JPEG)
        
        finally:
            self.camera.deinit()

    def _init_camera_video(self):
        # 其他设置：
        # 上翻下翻
        self.camera.flip(1)
        #左/右
        self.camera.mirror(1)

        # 分辨率
        self.camera.framesize(camera.FRAME_HVGA)
        # 选项如下：
        # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
        # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
        # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
        # FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
        # FRAME_P_FHD FRAME_QSXGA
        # 有关详细信息，请查看此链接：https://bit.ly/2YOzizz

        # 特效
        self.camera.speffect(camera.EFFECT_NONE)
        #选项如下：
        # 效果\无（默认）效果\负效果\ BW效果\红色效果\绿色效果\蓝色效果\复古效果
        # EFFECT_NONE (default) EFFECT_NEG \EFFECT_BW\ EFFECT_RED\ EFFECT_GREEN\ EFFECT_BLUE\ EFFECT_RETRO

        # 白平衡
        # camera.whitebalance(camera.WB_HOME)
        #选项如下：
        # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

        # 饱和
        self.camera.saturation(0)
        #-2,2（默认为0）. -2灰度
        # -2,2 (default 0). -2 grayscale 

        # 亮度
        self.camera.brightness(0)
        #-2,2（默认为0）. 2亮度
        # -2,2 (default 0). 2 brightness

        # 对比度
        self.camera.contrast(0)
        #-2,2（默认为0）.2高对比度
        #-2,2 (default 0). 2 highcontrast

        # 质量
        self.camera.quality(10)
        #10-63数字越小质量越高

        # socket UDP 的创建
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)

    def live_streaming_of_camera_feed(self,server_ip:str,server_port:int):
        # 初始化WiFi
        wifi = WiFiUtils()
        wifi.do_connect(WIFI_SSID, WIFI_PASSWORD)

        self._init_camera_video()

        try:
            while True:
                buf = self.camera.capture()  # 获取图像数据
                s.sendto(buf, (server_ip, port))  # 向服务器发送图像数据
                time.sleep(0.1)
        except:
            self.camera.deinit()
            self.camera.init(0, format=camera.JPEG)
        finally:
            self.camera.deinit()

    