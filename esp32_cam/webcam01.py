'''
Author: cuipu g050505@gmail.com
Date: 2023-05-20 09:40:04
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-07-26 11:04:22
FilePath: \esp32_projects\esp32_cam\webcam01.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''

import time, network, ntptime
from microdot import Microdot
from machine import Timer, Pin
import camera

(ST_INIT, ST_READY, ST_BUSY) = (300, 0, 100)

def toggle_led(led_pin):
    led_pin.value(not led_pin.value())

def led_blink_timed(timer, led_pin, state):
    if state == 'READY':
        timer.deinit()
        led_pin.value(ST_READY)
    elif state == 'INIT':
        timer.init(period=ST_INIT, mode=Timer.PERIODIC, callback=lambda t: toggle_led(led_pin))
    elif state == 'BUSY':
        timer.init(period=ST_BUSY, mode=Timer.PERIODIC, callback=lambda t: toggle_led(led_pin))
    else:
        print('not define yet')

# 声明引脚 D2 作为LED的引脚
led_pin = Pin(4, Pin.OUT)
timer = Timer(1)  # 创建定时器对象
# 定时器触发
led_blink_timed(timer, led_pin, state='INIT')


# 填上 Wi-Fi 连线信息
WIFI_SSID = 'AX6K-5G'
WIFI_PASSWORD = '1234567890...'

def connect_WiFi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config: ', wlan.ifconfig())

    ntptime.NTP_DELTA = ntptime.NTP_DELTA - 8*60*60 # UTC+8 
    ntptime.settime()
    print("同步后本地时间：%s" %str(time.localtime()))    

led_blink_timed(timer, led_pin, state='INIT')
# 连线 Wi-Fi
connect_WiFi()

app = Microdot()
@app.route('/')
def index(request):
    return 'Hello, world Microdot!'

@app.route('/image_feed')
def image_feed(request):
    timer = Timer(1)  # 创建定时器对象
    led_blink_timed(timer, led_pin, state='BUSY')
    while not camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM):
        time.sleep(1)    
    frame = camera.capture()
    camera.deinit()
    led_blink_timed(timer, led_pin, state='READY')
    return frame, 200, {'Content-Type': 'image/jpeg'}


if __name__ == '__main__':
    led_blink_timed(timer, led_pin, state='READY')
    app.run(debug=True) # 因为 Web 服务器属于阻断式服务，如果写在下方将无法运行

