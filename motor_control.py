# File: mower_control.py

import pygame
import serial
import time
import logging
from collections import deque
from typing import Deque
import kill_switch_control  # Importing the kill switch control module

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Setup serial communication
serialPort = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)

# Logging setup
logging.basicConfig(filename='mower_control.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Joystick setup
joystick = pygame.joystick.Joystick(0)
joystick.init()

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

def apply_deadzone(value: float, deadzone: float) -> float:
    return 0 if abs(value) < deadzone else value

def moving_average(history: Deque[float]) -> float:
    return sum(history) / len(history)

def process_joystick_input() -> None:
    global motor_left, motor_right

    pygame.event.pump()
    
    forward = joystick.get_axis(0)  # Forward/backward control
    steer = joystick.get_axis(1)    # Left/right control
    
    forward = apply_deadzone(forward, DEADZONE)
    steer = apply_deadzone(steer, DEADZONE)

    forward_history.append(forward)
    steer_history.append(steer)

    avg_forward = moving_average(forward_history)
    avg_steer = moving_average(steer_history)
    
    logging.debug(f"Raw Forward: {avg_forward}, Raw Steer: {avg_steer}")
    
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

def send_motor_command() -> None:
    packet = bytearray([motor_right, motor_left])
    serialPort.write(packet)
    logging.debug(f"Sending command: L{motor_left:02X} R{motor_right:02X}")

def main_loop() -> None:
    logging.info("Starting main loop. Move joystick to test.")
    try:
        while True:
            process_joystick_input()
            send_motor_command()
            kill_switch_control.process_kill_switch_input()  # Process kill switch input
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
