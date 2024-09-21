import smbus
import time
import math
import threading

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

# Initialize I2C bus
bus = smbus.SMBus(1)  # For Raspberry Pi Revision 2 and later (bus 1)

def MPU_Init():
    # Write to sample rate register
    bus.write_byte_data(DEVICE_ADDRESS, SMPLRT_DIV, 7)
    
    # Write to power management register to wake up MPU6050
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 1)
    
    # Write to Configuration register
    bus.write_byte_data(DEVICE_ADDRESS, CONFIG, 0)
    
    # Set Gyroscope to full scale range ±250deg/s
    bus.write_byte_data(DEVICE_ADDRESS, GYRO_CONFIG, 0)
    
    # Set Accelerometer to full scale range ±2g
    bus.write_byte_data(DEVICE_ADDRESS, ACCEL_CONFIG, 0)
    
    # Enable interrupt
    bus.write_byte_data(DEVICE_ADDRESS, INT_ENABLE, 1)

def read_raw_data(addr):
    # Read two bytes of data starting from addr
    high = bus.read_byte_data(DEVICE_ADDRESS, addr)
    low = bus.read_byte_data(DEVICE_ADDRESS, addr+1)
    
    # Combine high and low bytes
    value = ((high << 8) | low)
    # Convert to signed value
    if value > 32768:
        value = value - 65536
    return value

def calibrate_gyroscope():
    print("Calibrating gyroscope... Keep the device still.")
    num_readings = 100
    gx_bias = 0.0
    gy_bias = 0.0
    gz_bias = 0.0
    for i in range(num_readings):
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_XOUT_H+2)
        gyro_z = read_raw_data(GYRO_XOUT_H+4)
        
        gx_bias += gyro_x
        gy_bias += gyro_y
        gz_bias += gyro_z
        
        time.sleep(0.01)
    gx_bias /= num_readings
    gy_bias /= num_readings
    gz_bias /= num_readings
    # Convert to degrees per second
    gx_bias /= 131.0
    gy_bias /= 131.0
    gz_bias /= 131.0
    
    print("Calibration complete.")
    return gx_bias, gy_bias, gz_bias

# Functions to reset roll, pitch, yaw, and all
def reset_roll():
    global roll_offset
    roll_offset = current_roll

def reset_pitch():
    global pitch_offset
    pitch_offset = current_pitch

def reset_yaw():
    global yaw_offset
    yaw_offset = current_yaw

def reset_all():
    reset_roll()
    reset_pitch()
    reset_yaw()

def user_input():
    global running
    while running:
        cmd = input()
        if cmd == 'reset_roll':
            reset_roll()
            print("Roll angle reset.")
        elif cmd == 'reset_pitch':
            reset_pitch()
            print("Pitch angle reset.")
        elif cmd == 'reset_yaw':
            reset_yaw()
            print("Yaw angle reset.")
        elif cmd == 'reset_all':
            reset_all()
            print("All angles reset.")
        elif cmd == 'exit':
            running = False

# Initialize MPU6050
MPU_Init()
print("MPU6050 initialized")

# Calibrate gyroscope
gx_bias, gy_bias, gz_bias = calibrate_gyroscope()

# Variables for calculations
previous_time = time.time()
roll = 0.0
pitch = 0.0
yaw = 0.0
roll_offset = 0.0
pitch_offset = 0.0
yaw_offset = 0.0

# Start the user input thread
running = True
input_thread = threading.Thread(target=user_input)
input_thread.start()

try:
    while running:
        # Read accelerometer raw values
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_XOUT_H+2)
        acc_z = read_raw_data(ACCEL_XOUT_H+4)
        
        # Read gyroscope raw values
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_XOUT_H+2)
        gyro_z = read_raw_data(GYRO_XOUT_H+4)
        
        # Convert accelerometer values to g's
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        
        # Convert gyroscope values to degrees per second and subtract biases
        Gx = (gyro_x / 131.0) - gx_bias
        Gy = (gyro_y / 131.0) - gy_bias
        Gz = (gyro_z / 131.0) - gz_bias
        
        # Calculate roll and pitch from accelerometer data (in degrees)
        accel_roll = math.degrees(math.atan2(Ay, Az))
        accel_pitch = math.degrees(math.atan2(-Ax, math.sqrt(Ay*Ay + Az*Az)))
        
        # Calculate time elapsed
        current_time = time.time()
        dt = current_time - previous_time
        previous_time = current_time
        
        # Integrate gyroscope data to get angles
        gyro_roll = Gx * dt
        gyro_pitch = Gy * dt
        gyro_yaw = Gz * dt
        
        # Complementary filter to combine accelerometer and gyroscope data
        alpha = 0.96  # filter coefficient
        current_roll = alpha * (roll + gyro_roll) + (1 - alpha) * accel_roll
        current_pitch = alpha * (pitch + gyro_pitch) + (1 - alpha) * accel_pitch
        current_yaw = yaw + gyro_yaw  # No accelerometer correction for yaw
        
        # Update angles
        roll = current_roll
        pitch = current_pitch
        yaw = current_yaw
        
        # Apply offsets for resets
        display_roll = roll - roll_offset
        display_pitch = pitch - pitch_offset
        display_yaw = yaw - yaw_offset
        
        print("Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(display_roll, display_pitch, display_yaw))
        
        # Delay for stability
        time.sleep(0.01)
    
except KeyboardInterrupt:
    running = False
    print("\nProgram stopped by user")
