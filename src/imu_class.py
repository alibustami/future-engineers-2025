import smbus
import time
import math

class MPU6050Sensor:
    # MPU6050 Registers and their addresses
    PWR_MGMT_1   = 0x6B
    SMPLRT_DIV   = 0x19
    CONFIG       = 0x1A
    GYRO_CONFIG  = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE   = 0x38
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H  = 0x43

    # MPU6050 device address
    DEVICE_ADDRESS = 0x68  

    def __init__(self):
        # Initialize I2C bus
        self.bus = smbus.SMBus(1)  # For Raspberry Pi Revision 2 and later (bus 1)

        # Initialize sensor variables
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.previous_time = time.time()

        # Initialize gyroscope biases
        self.gx_bias = 0.0
        self.gy_bias = 0.0
        self.gz_bias = 0.0

        # Initialize MPU6050
        self.MPU_Init()
        print("MPU6050 initialized")

        # Calibrate gyroscope
        self.calibrate_gyroscope()

    def MPU_Init(self):
        # Write to sample rate register
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.SMPLRT_DIV, 7)
        
        # Write to power management register to wake up MPU6050
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.PWR_MGMT_1, 1)
        
        # Write to Configuration register
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.CONFIG, 0)
        
        # Set Gyroscope to full scale range ±250deg/s
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.GYRO_CONFIG, 0)
        
        # Set Accelerometer to full scale range ±2g
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.ACCEL_CONFIG, 0)
        
        # Enable interrupt (not used in this example)
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.INT_ENABLE, 1)

    def read_raw_data(self, addr):
        # Read two bytes of data starting from addr
        high = self.bus.read_byte_data(self.DEVICE_ADDRESS, addr)
        low = self.bus.read_byte_data(self.DEVICE_ADDRESS, addr+1)
        
        # Combine high and low bytes
        value = (high << 8) | low
        # Convert to signed value
        if value > 32767:
            value -= 65536
        return value

    def calibrate_gyroscope(self):
        print("Calibrating gyroscope... Keep the device still.")
        num_readings = 100
        gx_bias = 0.0
        gy_bias = 0.0
        gz_bias = 0.0
        for _ in range(num_readings):
            gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
            gyro_y = self.read_raw_data(self.GYRO_XOUT_H + 2)
            gyro_z = self.read_raw_data(self.GYRO_XOUT_H + 4)
            
            gx_bias += gyro_x
            gy_bias += gyro_y
            gz_bias += gyro_z
            
            time.sleep(0.01)
        gx_bias /= num_readings
        gy_bias /= num_readings
        gz_bias /= num_readings
        # Convert to degrees per second
        self.gx_bias = gx_bias / 131.0
        self.gy_bias = gy_bias / 131.0
        self.gz_bias = gz_bias / 131.0
        
        print("Calibration complete.")

    def update(self):
        # Read accelerometer raw values
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_XOUT_H + 2)
        acc_z = self.read_raw_data(self.ACCEL_XOUT_H + 4)
        
        # Read gyroscope raw values
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_XOUT_H + 2)
        gyro_z = self.read_raw_data(self.GYRO_XOUT_H + 4)
        
        # Convert accelerometer values to g's
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        
        # Convert gyroscope values to degrees per second and subtract biases
        Gx = (gyro_x / 131.0) - self.gx_bias
        Gy = (gyro_y / 131.0) - self.gy_bias
        Gz = (gyro_z / 131.0) - self.gz_bias
        
        # Calculate roll and pitch from accelerometer data (in degrees)
        accel_roll = math.degrees(math.atan2(Ay, Az))
        accel_pitch = math.degrees(math.atan2(-Ax, math.sqrt(Ay * Ay + Az * Az)))
        
        # Calculate time elapsed
        current_time = time.time()
        dt = current_time - self.previous_time
        self.previous_time = current_time
        
        # Integrate gyroscope data to get angles
        gyro_roll = Gx * dt
        gyro_pitch = Gy * dt
        gyro_yaw = Gz * dt
        
        # Complementary filter to combine accelerometer and gyroscope data
        alpha = 0.96  # filter coefficient
        self.roll = alpha * (self.roll + gyro_roll) + (1 - alpha) * accel_roll
        self.pitch = alpha * (self.pitch + gyro_pitch) + (1 - alpha) * accel_pitch
        self.yaw += gyro_yaw  # No accelerometer correction for yaw

    def get_angles(self):
        # Return the current roll, pitch, yaw angles
        return self.roll, self.pitch, self.yaw

import time

if __name__ == "__main__":
    sensor = MPU6050Sensor()

    try:
        while True:
            sensor.update()
            roll, pitch, yaw = sensor.get_angles()
            print("Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(roll, pitch, yaw))
            # Delay for stability
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
