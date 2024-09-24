# import smbus
# import time

# bus = smbus.SMBus(1)

# bus.write_byte(0x29,0x80|0x12)
# ver = bus.read_byte(0x29)
# if ver == 0x44:
#     print("Device found\n")
#     bus.write_byte(0x29, 0x80|0x00)
#     bus.write_byte(0x29, 0x01|0x02)
#     bus.write_byte(0x29, 0x80|0x14)
#     while True:
#         data = bus.read_i2c_block_data(0x29, 0)
#         clear = clear = data[1] << 8 | data[0]
#         red = data[3] << 8 | data[2]
#         green = data[5] << 8 | data[4]
#         blue = data[7] << 8 | data[6]
#         crgb = "C: %s, R: %s, G: %s B:%s\n" % (clear, red, green, blue)
#         print(crgb)
#         # print(data)
#         time.sleep(0.2)
# else:
#     print("Device not found\n")

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of the TCS34725 color sensor.
# Will detect the color from the sensor and print it out every second.


import time
import board
import adafruit_tcs34725
from src.sensors.sensor import Sensor
from typing import Tuple

class ColorSensor(Sensor):
    def __init__(self):
        i2c = board.I2C()          
        self.sensor = adafruit_tcs34725.TCS34725(i2c)

    def update(self):
        color_rgb: Tuple[int, int, int] = self.sensor.color_rgb_bytes
        color_hex = self.sensor.color
        return color_rgb, color_hex

if __name__ == "__main__":
    color_sn = ColorSensor()
    while True:
        rgb, _ = color_sn.update()
        print(rgb)

# # Create sensor object, communicating over the board's default I2C bus
# i2c = board.I2C()  # uses board.SCL and board.SDA
# # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
# sensor = adafruit_tcs34725.TCS34725(i2c)

# # Change sensor integration time to values between 2.4 and 614.4 milliseconds
# # sensor.integration_time = 150

# # Change sensor gain to 1, 4, 16, or 60
# # sensor.gain = 4

# # Main loop reading color and printing it every second.
# while True:
#     # Raw data from the sensor in a 4-tuple of red, green, blue, clear light component values
#     # print(sensor.color_raw)

#     color = sensor.color
#     color_rgb = sensor.color_rgb_bytes
#     print(
#         "RGB color as 8 bits per channel int: #{0:02X} or as 3-tuple: {1}".format(
#             color, color_rgb
#         )
#     )

#     # Read the color temperature and lux of the sensor too.
#     temp = sensor.color_temperature
#     lux = sensor.lux
#     print("Temperature: {0}K Lux: {1}\n".format(temp, lux))
#     # Delay for a second and repeat.
#     time.sleep(1.0)