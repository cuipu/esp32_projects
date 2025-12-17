# c_ha_temperature_sensor.py - 终极完整版（已加入上报间隔读取 + 安全容错 + 详细日志）
import ujson
import time
from umqtt.simple import MQTTClient
from c_utils import FileUtil

class HATemperatureSensor:
    def __init__(self):
        self.mqtt_client = None
        self.homeassistant_state_topic = None
        self.device_config_json = None
        self.temperature_send_msg_freq = 60  # 默认 60 秒

    def read_config_from_file(self):
        """读取配置文件并加载到字典"""
        file_util = FileUtil()
        config_str = file_util.read_file_as_json("esp32_config.txt")
        try:
            self.device_config_json = ujson.loads(config_str)
            print("[Config] 配置文件加载成功")
        except Exception as e:
            print("[Config] 配置文件解析失败，使用默认值:", e)
            self.device_config_json = {}

    def init_wifi(self):
        """连接 WiFi"""
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if wlan.isconnected():
            print("[WiFi] 已连接")
            return

        ssid = self.device_config_json.get("wifi_name", "unknown")
        pwd  = self.device_config_json.get("wifi_password", "")
        print(f"[WiFi] 正在连接 {ssid} ...")
        wlan.connect(ssid, pwd)

        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if wlan.isconnected():
            print("[WiFi] 连接成功")
        else:
            print("[WiFi] 连接失败")

    def init_mqtt(self):
        """安全连接 MQTT"""
        try:
            print("[MQTT] 正在连接服务器...")
            self.mqtt_client = MQTTClient(
                client_id=self.device_config_json.get("homeassistant_device_name", "esp32-unknown"),
                server=self.device_config_json.get("mqtt_server", "127.0.0.1"),
                port=int(self.device_config_json.get("mqtt_port", 1883)),
                user=self.device_config_json.get("mqtt_user", ""),
                password=self.device_config_json.get("mqtt_password", ""),
                keepalive=int(self.device_config_json.get("mqtt_keepalive", 60))
            )
            self.mqtt_client.connect()
            print("[MQTT] 连接成功")
        except Exception as e:
            print("[MQTT] 连接失败:", e)
            self.mqtt_client = None

    def init_ha_device_info(self):
        """初始化 HA 自动发现信息 + 读取上报间隔"""
        if not self.device_config_json:
            print("[HA] 配置未加载，跳过注册")
            return

        dev_name    = self.device_config_json.get("homeassistant_device_name", "esp32-device")
        sensor_name = self.device_config_json.get("homeassistant_sensor_name", "sensor")
        sensor_type = self.device_config_json.get("homeassistant_sensor_type", "temperature")

        # 读取上报间隔（单位秒）
        self.temperature_send_msg_freq = float(
            self.device_config_json.get("temperature_send_msg_freq", 60)
        )
        print(f"[Config] 上报间隔设为 {self.temperature_send_msg_freq} 秒")

        # state topic（上报温度用）
        self.homeassistant_state_topic = f"{dev_name}/{sensor_name}/state"

        # config topic（HA 自动发现必须的固定格式！）
        #config_topic = "homeassistant/sensor/{}/config".format(sensor_name)
        #config_topic = "homeassistant/sensor/{}/{}/config".format(dev_name, sensor_name)
        config_topic = f"homeassistant/sensor/{dev_name}/{sensor_name}/config"
        print(f"[HA] 自动发现消息已发送 config_topic → {config_topic}")
        #config_topic = "homeassistant/sensor/HA/HA-{}-{}/config".format(dev_name, sensor_name)


        # n = name
        # 使用unique_id缩写键名 uniq_id 也可以
        # 使用state_topic缩写键名 stat_t 减小体积
        # 缩写 identifiers -> ids
        # 缩写 manufacturer -> mf
        
        payload = {
            "n": sensor_type, 
            "uniq_id": f"{dev_name}_{sensor_name}",  
            "stat_t": self.homeassistant_state_topic, 
            "dev_cla": "temperature",
            # "unit_of_measurement": "℃",  # 注意这个数据在ESP32中会导致发送失败，即℃符号导致发送失败，所以不要发这种数据
            # "command_topic": self.command_topic,
            "icon": "mdi:thermometer",
            "device": {
                "ids": [dev_name], 
                "name": dev_name,
                "mf": "ESP32",  
                "sw_version": "1.0"
            }
        }
        
        if self.mqtt_client:
            try:
                self.mqtt_client.publish(config_topic, ujson.dumps(payload), retain=True)
                print(f"[HA] 自动发现消息已发送 → payload f{payload}")
                print(f"[HA] 实体将在 HA 中显示为: {sensor_type}")
                
            except Exception as e:
                print("[HA] 发送自动发现消息失败:", e)
        else:
            print("[HA] MQTT 未连接，跳过自动发现注册")

    def do_mqtt_publish_device_msg(self, msg):
        """上报温度到 HA"""
        if self.mqtt_client:
            try:
                self.mqtt_client.publish(self.homeassistant_state_topic, str(msg))
                print(f"[HA] 上报温度: {msg}°C")
            except Exception as e:
                print("[HA] 上报失败:", e)
        else:
            print("[HA] MQTT 未连接，跳过上报")
            
    def start_device(self):
        """主循环：读取温度、上报 HA、使用配置频率控制间隔"""
        while True:
            try:
                device, temperature = self.ds18b20_temperature_sensor.collect_temperature_result()
                print('{} temperature: {} ℃'.format(device, temperature))

                # 上报到 HA
                self.do_mqtt_publish_device_msg(str(temperature))

                # 超温报警
                if temperature > 60:
                    self.passive_buzzer.play_mario()

                # 使用配置里的频率（单位秒）
                time.sleep(self.temperature_send_msg_freq)

            except Exception as e:
                print("start_device 异常:", e)
                time.sleep(5)  # 出错了等 5 秒再继续
