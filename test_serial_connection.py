import serial
import time

# Replace /dev/ttyUSB0 with the correct device name if it's different
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    ser.write(b'Hello, Serial!\n')
    time.sleep(1)
    while ser.in_waiting > 0:
        print(ser.readline().decode('utf-8').strip())
    ser.close()
except serial.SerialException as e:
    print(f"Error: {e}")
