# File: mower_control.py

import pygame
import serial
import RPi.GPIO as GPIO
import time

# Constants
SERVO_PIN = 18
BACKUP_DISTANCE = 2  # feet
GPS_SERIAL_PORT = '/dev/ttyUSB0'
MOTOR_SERIAL_PORT = '/dev/ttyUSB1'
SERVO_ON = 7.5  # Duty cycle to turn on servo
SERVO_OFF = 0  # Duty cycle to turn off servo

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
gps_serial = serial.Serial(GPS_SERIAL_PORT, 9600, timeout=1)
motor_serial = serial.Serial(MOTOR_SERIAL_PORT, 9600, timeout=1)

# Mapping variables
mapping_mode = False
obstacle_mode = False
current_position = (0.0, 0.0)
grid = [[0 for _ in range(100)] for _ in range(100)]  # Example 100x100 grid

def update_motor_control(x, y):
    try:
        motor_serial.write(f'X{x}Y{y}\n'.encode())
    except serial.SerialException as e:
        print(f"Error sending motor control data: {e}")

def update_gps_position():
    global current_position
    try:
        line = gps_serial.readline().decode('utf-8')
        if line.startswith('$GNGGA'):
            parts = line.split(',')
            lat = float(parts[2])
            lon = float(parts[4])
            current_position = (lat, lon)
    except (serial.SerialException, ValueError, IndexError) as e:
        print(f"Error reading GPS data: {e}")

def handle_buttons():
    global mapping_mode, obstacle_mode
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button
                mapping_mode = not mapping_mode
                print("Mapping mode:", mapping_mode)
            elif event.button == 1:  # B button
                obstacle_mode = not obstacle_mode
                print("Obstacle mode:", obstacle_mode)
            elif event.button == 2:  # X button
                stop_and_backup()
            elif event.button == 3:  # Y button
                toggle_mower()

def stop_and_backup():
    print("Stopping and backing up")
    update_motor_control(0, 0)
    time.sleep(1)
    update_motor_control(-1, -1)
    time.sleep(BACKUP_DISTANCE / 2.0)
    update_motor_control(0, 0)

def toggle_mower():
    print("Toggling mower")
    servo.ChangeDutyCycle(SERVO_ON)
    time.sleep(1)
    servo.ChangeDutyCycle(SERVO_OFF)

def main():
    while True:
        handle_buttons()
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
        print("Exiting program")
    finally:
        servo.stop()
        GPIO.cleanup()
        gps_serial.close()
        motor_serial.close()
        pygame.quit()
