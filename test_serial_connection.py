import serial
import time

def test_serial_connection(port):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        ser.flush()

        if ser.isOpen():
            print(f"Serial port {port} is open and ready.")

            # Test by sending a simple command
            ser.write(b'TEST\n')
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').rstrip()
                print(f"Received: {response}")

        ser.close()

    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_serial_connection('/dev/ttyS0')  # Replace with your serial port
