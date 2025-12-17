# main.py - 推荐版：LCD 实时显示时间 + 温度 + 网络状态
import time
from c_devices import LCD1602, DS18B20, PassiveBuzzer
from c_ha_temperature_sensor import HATemperatureSensor

# 初始化硬件
lcd = LCD1602()
temp_sensor = DS18B20()
buzzer = PassiveBuzzer(23)

# 初始化 HA
ha = None
wifi_ok = False
mqtt_ok = False

try:
    ha = HATemperatureSensor()
    ha.read_config_from_file()
    ha.init_wifi()
    wifi_ok = True
    ha.init_mqtt()
    ha.init_ha_device_info()
    mqtt_ok = True
    print("[HA] 初始化成功")
except Exception as e:
    print("[HA] 初始化失败:", e)

# 开机显示
lcd.clear()
if wifi_ok and mqtt_ok:
    lcd.print("System Ready", "HA Connected")
elif wifi_ok:
    lcd.print("WiFi OK", "MQTT Failed")
else:
    lcd.print("No WiFi", "Offline Mode")
time.sleep(3)

# 主循环（每秒刷新 LCD + 按配置频率上报）
last_report_time = 0
report_interval = 60  # 默认 60 秒

if ha and ha.device_config_json:
    report_interval = float(ha.device_config_json.get("temperature_send_msg_freq", 60))

last_connect_try = 0
CONNECT_INTERVAL = 600  # 10 分钟重连一次

print("开始主循环...")

def get_local_time_str():
    """获取北京时间字符串 (UTC+8)"""
    utc = time.time()
    beijing = utc + 8 * 3600  # 加 8 小时
    t = time.localtime(beijing)
    return f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"


while True:
    try:
        current_time = time.time()

        # 每10分钟重连一次
        if current_time - last_connect_try >= CONNECT_INTERVAL:
            print("[系统] 尝试重连...")
            try:
                if ha:
                    ha.init_wifi()
                    wifi_ok = True
                    ha.init_mqtt()
                    mqtt_ok = True
            except:
                wifi_ok = False
                mqtt_ok = False
            last_connect_try = current_time

        # 读取温度
        temp = temp_sensor.read_temp()
        time_str = get_local_time_str()
        
        # WiFi 状态显示
        wifi_status = "WiFi OK" if wifi_ok else "No WiFi"
        if temp is not None:
            temp_str = f"{temp:5.1f}C"

            # 按配置频率上报
            if current_time - last_report_time >= report_interval:
                if ha and wifi_ok and mqtt_ok:
                    try:
                        ha.do_mqtt_publish_device_msg(str(temp))
                        ha_status = "HA OK"
                    except:
                        ha_status = "HA Fail"
                else:
                    ha_status = "No HA"
                last_report_time = current_time
            else:
                ha_status = "HA OK" if (ha and wifi_ok and mqtt_ok) else "No HA"

            lcd.print(time_str + wifi_status, f" {temp_str} "+ ha_status)

            if temp > 60:
                buzzer.play_mario()
        else:
            lcd.print(time_str, "Temp Error")

        time.sleep(1)

    except Exception as e:
        print("异常:", e)
        lcd.print("Error", "Running...")
        time.sleep(5)
