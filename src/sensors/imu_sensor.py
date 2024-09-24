
from src.sensors.sensor import Sensor
import smbus
from imusensor.MPU9250 import MPU9250
class IMUSeneor(Sensor):
    def __init__(self, address):
        self.address = address
        bus = smbus.SMBus(1)
        self.imu = MPU9250.MPU9250(bus, address)
        self.imu.begin()
    def update(self):
        self.imu.readSensor()
        self.imu.computeOrientation()

        return (self.imu.roll, self.imu.pitch, self.imu.yaw)
          
sensor = IMUSeneor(0x68)
while True:
    print(sensor.update())
