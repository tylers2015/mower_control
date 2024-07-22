
import serial
import time

# Define constants
MOTOR_SERIAL_PORT = '/dev/ttyUSB0'  # Update with the correct serial port
BAUD_RATE = 9600

# Function to send command to motor driver
def send_motor_command(serial_port, motor, direction, speed):
    command = (motor << 7) | (direction << 6) | speed
    serial_port.write(bytes([command]))

# Initialize serial port
def init_serial(port, baudrate):
    try:
        return serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return None
