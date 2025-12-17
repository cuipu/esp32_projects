# boot.py
import network
import time
import ntptime

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("正在连接 WiFi...")
    wlan.connect("AX6K", "1234567890...")  # 改成你的WiFi
    for _ in range(20):
        if wlan.isconnected():
            break
        time.sleep(1)

if wlan.isconnected():
    print("WiFi 已连接:", wlan.ifconfig())
    try:
        ntptime.settime()
        print("时间同步成功")
    except:
        print("时间同步失败")
else:
    print("WiFi 连接失败（main.py 会自动重试）")

print("boot.py 完成 → 启动 main.py")
