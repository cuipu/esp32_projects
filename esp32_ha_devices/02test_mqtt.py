from umqttsimple import MQTTClient
from c_utils import WiFiUtils
import time

# WiFi配置
WIFI_NAME = 'TP-LINK_502_2.4G'
WIFI_PASSWORD = '1234567890...'

# MQTT 服务器配置
MQTT_SERVER = '192.168.2.80'
MQTT_PORT = 1883
MQTT_USER = 'test'
MQTT_PASSWORD = '1234560.'
MQTT_KEEPALIVE = 60


def mqtt_test():

    wifi = WiFiUtils()
    wifi.do_connect(WIFI_NAME, WIFI_PASSWORD)
    '''
    description: 初始化mqtt
    return {*}
    '''
    # 建立一个MQTT客户端
    mqtt_client = MQTTClient("test", MQTT_SERVER,
                             MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_KEEPALIVE)

    # 建立连接
    mqtt_client.connect()

    mqtt_client.subscribe('test')
    mqtt_client.set_callback(sub_callback)

    i = 0
    while True:
        mqtt_client.publish("test", i)
        i += 1
        print(i)
        time.sleep(1)


def sub_callback(topic, msg):
    print(topic, msg)


def main():
    mqtt_test()


if __name__ == "__main__":
    main()
