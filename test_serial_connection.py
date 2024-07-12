import serial
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600  # Ensure this matches your DIP switch settings

try:
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    # Send a simple command, this should be replaced with a valid command for your controller
    ser.write(b'V')  # Example command to read version or status
    
    time.sleep(1)  # Wait for the response
    
    while ser.in_waiting > 0:
        print(ser.readline().decode('utf-8').strip())
    
    ser.close()
except serial.SerialException as e:
    print(f"Error: {e}")
