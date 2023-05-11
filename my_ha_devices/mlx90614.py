'''
Author: cuipu g050505@gmail.com
Date: 2023-05-05 23:03:28
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-05-09 19:12:31
FilePath: \Demo\my_ha_devices\mlx90614.py
Description: 

Copyright (c) 2023 by Mr.Cui, All Rights Reserved. 
'''
import machine
from machine import I2C


class MLX90614:
    def __init__(self, i2c, address=0x5A):
        self.i2c = i2c
        self.address = address

    def read_object_temp(self):
        return self.read_temp(0x07)

    def read_ambient_temp(self):
        return self.read_temp(0x06)

    def read_temp(self, register):
        self.i2c.writeto(self.address, bytes([register]))
        raw_data = self.i2c.readfrom(self.address, 3)
        data = bytearray([raw_data[1], raw_data[0]])
        return (data[0] + (data[1] << 8)) * 0.02 - 273.15
