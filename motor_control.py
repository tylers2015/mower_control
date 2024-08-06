import os
import logging
import pygame
import serial
import time
from collections import deque
from typing import Deque
import kill_switch_control

# Define constants
MOTOR_SERIAL_PORT = '/dev/serial0'  # Using built-in UART
BAUD_RATE = 9600

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Logging setup
logging.basicConfig(filename='/home/ty/motor_control/mower_control.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting motor control script")

def initialize_joystick():
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        logging.info(f"Joystick initialized: {joystick.get_name()}")
        return joystick
    else:
        logging.error("No joysticks found. Waiting for joystick connection...")
        return None

# Motor control variables
motor_left = 0
motor_right = 0

# Calibration threshold to handle joystick drift
DEADZONE = 0.1

# Motor trim adjustments
LEFT_TRIM = 0
RIGHT_TRIM = 0

# Speed scaling factor to reduce speed
SPEED_SCALE = 70

# Moving average filter parameters
FILTER_SIZE = 3
forward_history: Deque[float] = deque([0] * FILTER_SIZE, maxlen=FILTER_SIZE)
steer_history: Deque[float] = deque([0] * FILTER_SIZE, maxlen=FILTER_SIZE)

# Button constants
VIEW_BUTTON = 10
SHUTDOWN_HOLD_TIME = 3

def apply_deadzone(value: float, deadzone: float) -> float:
    return 0 if abs(value) < deadzone else value

def moving_average(history: Deque[float]) -> float:
    return sum(history) / len(history)

def reset_motors(serial_port) -> None:
    logging.info("Resetting motors.")
    try:
        send_motor_command(serial_port, 0, 0, 0)
        send_motor_command(serial_port, 1, 0, 0)
        logging.info("Motors reset successfully.")
    except serial.SerialException as e:
        logging.error(f"Failed to reset motors: {e}")

def send_motor_command(serial_port, motor, direction, speed):
    command = ((motor << 7) | (direction << 6) | speed) & 0xFF
    try:
        serial_port.write(bytes([command]))
        logging.debug(f'Sent command to motor {motor}: direction={direction}, speed={speed}')
    except serial.SerialException as e:
        logging.error(f"Failed to send command to motor {motor}: {e}")

def process_joystick_input(joystick) -> None:
    global motor_left, motor_right

    pygame.event.pump()
    
    forward = joystick.get_axis(0)
    steer = joystick.get_axis(1)
    
    logging.debug(f"Joystick axis - Forward: {forward}, Steer: {steer}")
    
    forward = apply_deadzone(forward, DEADZONE)
    steer = apply_deadzone(steer, DEADZONE)
    
    logging.debug(f"Joystick axis after deadzone - Forward: {forward}, Steer: {steer}")

    forward_history.append(forward)
    steer_history.append(steer)

    avg_forward = moving_average(forward_history)
    avg_steer = moving_average(steer_history)
    
    logging.debug(f"Moving average - Forward: {avg_forward}, Steer: {avg_steer}")
    
    left_speed = (avg_forward + avg_steer) * SPEED_SCALE + LEFT_TRIM
    right_speed = (avg_forward - avg_steer) * SPEED_SCALE + RIGHT_TRIM
    
    left_speed = max(min(left_speed, 63), -63)
    right_speed = max(min(right_speed, 63), -63)
    
    motor_left = int(abs(left_speed)) & 63
    motor_right = int(abs(right_speed)) & 63
    
    if left_speed < 0:
        motor_left |= 64
    else:
        motor_left &= 63
        
    if right_speed < 0:
        motor_right |= 192
    else:
        motor_right |= 128
    
    logging.debug(f"Processed Left Motor: {motor_left}, Processed Right Motor: {motor_right}")
    
    send_motor_command(serialPort, 0, motor_left >> 6, motor_left & 63)
    send_motor_command(serialPort, 1, motor_right >> 6, motor_right & 63)

def shutdown_pi() -> None:
    logging.info("Shutting down Raspberry Pi.")
    os.system("sudo shutdown -h now")

def initialize_serial_port(port, baud_rate, retries=5, delay=5):
    for attempt in range(retries):
        try:
            ser = serial.Serial(port, baud_rate, timeout=0.5)
            logging.info(f"Successfully initialized serial port {port}")
            return ser
        except serial.SerialException as e:
            logging.error(f"Attempt {attempt + 1} - Failed to initialize serial port {port}: {e}")
            time.sleep(delay)
    logging.error(f"Failed to initialize serial port {port} after {retries} attempts")
    return None

def main_loop() -> None:
    logging.info("Starting main loop. Move joystick to test.")
    view_button_pressed_time = None

    global serialPort
    serialPort = initialize_serial_port(MOTOR_SERIAL_PORT, BAUD_RATE)

    if serialPort is None:
        logging.error("Exiting due to failure in initializing motor serial port")
        exit(1)

    reset_motors(serialPort)

    joystick = initialize_joystick()

    try:
        while True:
            if joystick is None:
                joystick = initialize_joystick()
                time.sleep(1)
                continue

            process_joystick_input(joystick)
            kill_switch_control.process_kill_switch_input()

            view_button_state = joystick.get_button(VIEW_BUTTON)
            logging.debug(f"View button state: {view_button_state}")

            if view_button_state:
                if view_button_pressed_time is None:
                    view_button_pressed_time = time.time()
                    logging.debug("View button pressed.")
                else:
                    elapsed_time = time.time() - view_button_pressed_time
                    logging.debug(f"View button held for {elapsed_time} seconds.")
                    if elapsed_time >= SHUTDOWN_HOLD_TIME:
                        logging.debug(f"View button held for {SHUTDOWN_HOLD_TIME} seconds, shutting down.")
                        shutdown_pi()
            else:
                if view_button_pressed_time is not None:
                    logging.debug("View button released.")
                view_button_pressed_time = None

            time.sleep(0.05)
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
        serialPort.write(bytearray([128, 128]))
    finally:
        kill_switch_control.pwm.stop()
        kill_switch_control.GPIO.cleanup()

if __name__ == "__main__":
    main_loop()