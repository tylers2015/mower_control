import serial
import time
import logging
import pynmea2
import RPi.GPIO as GPIO
from xbox_controller import XboxController

# Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Ensure this is the correct port
BAUD_RATE = 9600  # Ensure this matches your DIP switch settings
LOG_FILE = 'mower_control.log'
GPIO_SERVO_PIN = 17  # Example GPIO pin for servo control

# Initialize logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

# Initialize GPIO for servo control
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(GPIO_SERVO_PIN, 50)  # 50 Hz
servo.start(7.5)  # Neutral position

# Initialize Xbox controller
xbox_controller = XboxController()

def initialize_motor_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        logging.info("Motor serial initialized")
        return ser
    except serial.SerialException as e:
        logging.error(f"Failed to initialize motor serial: {e}")
        return None

def update_motor_control(ser, joystick_input):
    command = f"X:{joystick_input['x']} Y:{joystick_input['y']}"
    try:
        ser.write(command.encode())
        logging.info(f"Sent command: {command}")
    except serial.SerialException as e:
        logging.error(f"Failed to send command: {e}")

def read_gps_data(ser):
    try:
        data = ser.readline().decode('utf-8').strip()
        if data.startswith('$GPGGA'):
            msg = pynmea2.parse(data)
            logging.info(f"GPS Data: {msg}")
            return msg
    except serial.SerialException as e:
        logging.error(f"Failed to read GPS data: {e}")
    except pynmea2.ParseError as e:
        logging.error(f"Failed to parse GPS data: {e}")
    return None

def main():
    motor_serial = initialize_motor_serial()
    gps_serial = initialize_motor_serial()  # Assuming GPS is on the same serial settings
    if not motor_serial or not gps_serial:
        logging.error("Serial initialization failed. Exiting.")
        return

    try:
        while True:
            joystick_input = xbox_controller.get_joystick()
            update_motor_control(motor_serial, joystick_input)
            gps_data = read_gps_data(gps_serial)
            if gps_data:
                print(f"Latitude: {gps_data.latitude}, Longitude: {gps_data.longitude}")

            time.sleep(0.1)  # Adjust loop frequency as needed

    except KeyboardInterrupt:
        logging.info("Exiting program")
    finally:
        motor_serial.close()
        gps_serial.close()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
