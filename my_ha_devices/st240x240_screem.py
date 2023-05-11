'''
Author: cuipu g050505@gmail.com
Date: 2023-04-27 23:16:31
LastEditors: cuipu g050505@gmail.com
LastEditTime: 2023-04-28 11:08:14
FilePath: \Demo\st240x240_screem.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from uQR import QRCode
from machine import Pin, SPI
import st7789_itprojects


tft = st7789_itprojects.ST7889_Image(
    SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))
tft.fill(st7789_itprojects.color565(255, 255, 255))  # 背景设置为白色


qr = QRCode(border=2)
qr.add_data('王铭东')
matrix = qr.get_matrix()

row_len = len(matrix)
col_len = len(matrix[0])

print("row=%d, col=%d" % (row_len, col_len))

# 放大倍数
SCALE_RATE = 8

# 准备黑色，白色数据
buffer_black = bytearray(SCALE_RATE * SCALE_RATE * 2)  # 每个点pixel有2个字节表示颜色
buffer_white = bytearray(SCALE_RATE * SCALE_RATE * 2)  # 每个点pixel有2个字节表示颜色
color_black = st7789_itprojects.color565(0, 0, 0)
color_black_byte1 = color_black & 0xff00 >> 8
color_black_byte2 = color_black & 0xff
color_white = st7789_itprojects.color565(255, 255, 255)
color_white_byte1 = color_white & 0xff00 >> 8
color_white_byte2 = color_white & 0xff

for i in range(0, SCALE_RATE * SCALE_RATE * 2, 2):
    buffer_black[i] = color_black_byte1
    buffer_black[i + 1] = color_black_byte2
    buffer_white[i] = color_white_byte1
    buffer_white[i + 1] = color_white_byte2

# 循环次数不增加，只增加每次发送的数据量，每次发送SCALE_RATE X SCALE_RATE个点的信息
for row in range(row_len):
    for col in range(col_len):
        if matrix[row][col]:
            # tft.pixel(row, col, st7789_itprojects.color565(0, 0, 0))
            tft.show_img(row * SCALE_RATE, col * SCALE_RATE, row * SCALE_RATE +
                         SCALE_RATE - 1, col * SCALE_RATE + SCALE_RATE - 1, buffer_black)
        else:
            # tft.pixel(row, col, st7789_itprojects.color565(255, 255, 255))
            tft.show_img(row * SCALE_RATE, col * SCALE_RATE, row * SCALE_RATE +
                         SCALE_RATE - 1, col * SCALE_RATE + SCALE_RATE - 1, buffer_white)
        col += 1

    row += 1
