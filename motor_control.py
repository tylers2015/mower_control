# File: motor_control.py

import pygame
import serial
import time
import logging
from collections import deque
from typing import Deque
import os
import kill_switch_control  # Importing the kill switch control module

# Define constants
MOTOR_SERIAL_PORT = '/dev/ttyUSB0'  # Update with the correct serial port
BAUD_RATE = 9600

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Setup serial communication
serialPort = serial.Serial(MOTOR_SERIAL_PORT, BAUD_RATE, timeout=0.5)

# Logging setup
logging.basicConfig(filename='mower_control.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Check for joystick availability
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    logging.info(f"Joystick initialized: {joystick.get_name()}")
else:
    logging.error("No joysticks found. Exiting.")
    exit(1)

# Motor control variables
motor_left = 0
motor_right = 0

# Calibration threshold to handle joystick drift
DEADZONE = 0.1

# Motor trim adjustments
LEFT_TRIM = 0
RIGHT_TRIM = 0

# Speed scaling factor to reduce speed
SPEED_SCALE = 70  # Reduced value to decrease speed

# Moving average filter parameters
FILTER_SIZE = 3
forward_history: Deque[float] = deque([0] * FILTER_SIZE, maxlen=FILTER_SIZE)
steer_history: Deque[float] = deque([0] * FILTER_SIZE, maxlen=FILTER_SIZE)

# Button constants
VIEW_BUTTON = 10  # Button index for shutdown
SHUTDOWN_HOLD_TIME = 3  # Time in seconds to hold the button for shutdown

def apply_deadzone(value: float, deadzone: float) -> float:
    return 0 if abs(value) < deadzone else value

def moving_average(history: Deque[float]) -> float:
    return sum(history) / len(history)

def reset_motors(serial_port) -> None:
    logging.info("Resetting motors.")
    try:
        send_motor_command(serial_port, 0, 0, 0)  # Motor Left
        send_motor_command(serial_port, 1, 0, 0)  # Motor Right
        logging.info("Motors reset successfully.")
    except serial.SerialException as e:
        logging.error(f"Failed to reset motors: {e}")

def send_motor_command(serial_port, motor, direction, speed):
    command = ((motor << 7) | (direction << 6) | speed) & 0xFF
    serial_port.write(bytes([command]))

def process_joystick_input() -> None:
    global motor_left, motor_right

    pygame.event.pump()
    
    forward = joystick.get_axis(0)  # Forward/backward control
    steer = joystick.get_axis(1)    # Left/right control
    
    logging.debug(f"Joystick axis - Forward: {forward}, Steer: {steer}")
    
    forward = apply_deadzone(forward, DEADZONE)
    steer = apply_deadzone(steer, DEADZONE)
    
    logging.debug(f"Joystick axis after deadzone - Forward: {forward}, Steer: {steer}")

    forward_history.append(forward)
    steer_history.append(steer)

    avg_forward = moving_average(forward_history)
    avg_steer = moving_average(steer_history)
    
    logging.debug(f"Moving average - Forward: {avg_forward}, Steer: {avg_steer}")
    
    # Calculate motor speeds for zero-turn steering with increased speed
    left_speed = (avg_forward + avg_steer) * SPEED_SCALE + LEFT_TRIM
    right_speed = (avg_forward - avg_steer) * SPEED_SCALE + RIGHT_TRIM
    
    # Normalize motor speeds
    left_speed = max(min(left_speed, 63), -63)
    right_speed = max(min(right_speed, 63), -63)
    
    motor_left = int(abs(left_speed)) & 63
    motor_right = int(abs(right_speed)) & 63
    
    if left_speed < 0:
        motor_left |= 64  # Reverse bit for left motor
    else:
        motor_left &= 63  # Forward for left motor
        
    if right_speed < 0:
        motor_right |= 192  # Reverse bit for right motor
    else:
        motor_right |= 128  # Forward for right motor
    
    logging.debug(f"Processed Left Motor: {motor_left}, Processed Right Motor: {motor_right}")
    
    send_motor_command(serialPort, 0, motor_left >> 6, motor_left & 63)
    send_motor_command(serialPort, 1, motor_right >> 6, motor_right & 63)

def shutdown_pi() -> None:
    logging.info("Shutting down Raspberry Pi.")
    os.system("sudo shutdown -h now")

def main_loop() -> None:
    logging.info("Starting main loop. Move joystick to test.")
    view_button_pressed_time = None

    # Reset motors at startup
    reset_motors(serialPort)

    try:
        while True:
            process_joystick_input()
            kill_switch_control.process_kill_switch_input()  # Process kill switch input

            # Check the view button state
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

            time.sleep(0.05)  # Reduced delay to improve responsiveness
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
        # Send stop command to ensure motors are stopped
        serialPort.write(bytearray([128, 128]))  # Stop motors
    finally:
        kill_switch_control.pwm.stop()
        kill_switch_control.GPIO.cleanup()

if __name__ == "__main__":
    main_loop()