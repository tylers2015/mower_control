import pygame
import serial
import RPi.GPIO as GPIO
import time
import logging
import pynmea2

# Constants
SERVO_PIN = 18
BACKUP_DISTANCE = 2  # feet
GPS_SERIAL_PORT = '/dev/ttyUSB0'
MOTOR_SERIAL_PORT = '/dev/ttyUSB1'
SERVO_ON = 7.5  # Duty cycle to turn on servo
SERVO_OFF = 0  # Duty cycle to turn off servo
EMERGENCY_STOP_BUTTON = 4  # Designated button for emergency stop

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# Initialize Pygame for Xbox controller
pygame.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()

# Initialize Serial for GPS and Motor controller
try:
    gps_serial = serial.Serial(GPS_SERIAL_PORT, 9600, timeout=1)
    motor_serial = serial.Serial(MOTOR_SERIAL_PORT, 9600, timeout=1)
except serial.SerialException as e:
    logging.error(f"Could not open serial port: {e}")
    exit(1)

# Mapping variables
mapping_mode = False
obstacle_mode = False
current_position = (0.0, 0.0)
grid = [[0 for _ in range(100)] for _ in range(100)]  # Example 100x100 grid
emergency_stop = False

def update_motor_control(x, y):
    try:
        motor_serial.write(f'X{x}Y{y}\n'.encode())
        logging.info(f'Motor control updated: X={x}, Y={y}')
    except serial.SerialException as e:
        logging.error(f"Error sending motor control data: {e}")

def update_gps_position():
    global current_position
    try:
        line = gps_serial.readline().decode('utf-8')
        if line.startswith('$GNGGA'):
            msg = pynmea2.parse(line)
            lat = msg.latitude
            lon = msg.longitude
            current_position = (lat, lon)
            logging.info(f'GPS position updated: Latitude={lat}, Longitude={lon}')
    except (serial.SerialException, pynmea2.ParseError) as e:
        logging.error(f"Error reading GPS data: {e}")

def handle_buttons():
    global mapping_mode, obstacle_mode, emergency_stop
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == EMERGENCY_STOP_BUTTON:  # Emergency stop
                emergency_stop = True
                update_motor_control(0, 0)
                logging.warning("Emergency stop activated!")
            elif event.button == 0:  # A button
                mapping_mode = not mapping_mode
                logging.info(f"Mapping mode: {mapping_mode}")
            elif event.button == 1:  # B button
                obstacle_mode = not obstacle_mode
                logging.info(f"Obstacle mode: {obstacle_mode}")
            elif event.button == 2:  # X button
                stop_and_backup()
            elif event.button == 3:  # Y button
                toggle_mower()

def stop_and_backup():
    logging.info("Stopping and backing up")
    update_motor_control(0, 0)
    time.sleep(1)
    update_motor_control(-1, -1)
    time.sleep(BACKUP_DISTANCE / 2.0)
    update_motor_control(0, 0)

def toggle_mower():
    logging.info("Toggling mower")
    servo.ChangeDutyCycle(SERVO_ON)
    time.sleep(1)
    servo.ChangeDutyCycle(SERVO_OFF)

def main():
    while True:
        handle_buttons()
        if emergency_stop:
            logging.warning("Emergency stop is active, stopping operations.")
            continue
        x = controller.get_axis(0)
        y = controller.get_axis(1)
        update_motor_control(x, y)
        update_gps_position()
        if mapping_mode:
            grid[int(current_position[0])][int(current_position[1])] = 1
        if obstacle_mode:
            grid[int(current_position[0])][int(current_position[1])] = -1
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting program")
    finally:
        servo.stop()
        GPIO.cleanup()
        gps_serial.close()
        motor_serial.close()
        pygame.quit()
