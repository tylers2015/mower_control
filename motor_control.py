# File: mower_control.py

import pygame
import serial
import time
import logging
from collections import deque

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
motorLeft = 0
motorRight = 0

# Calibration threshold to handle joystick drift
DEADZONE = 0.1

# Motor trim adjustments
left_trim = 0
right_trim = 0

# Speed scaling factor to reduce speed
SPEED_SCALE = 70  # Reduced value to decrease speed

# Moving average filter parameters
FILTER_SIZE = 3
forward_history = deque([0]*FILTER_SIZE, maxlen=FILTER_SIZE)
steer_history = deque([0]*FILTER_SIZE, maxlen=FILTER_SIZE)

def apply_deadzone(value, deadzone):
    if abs(value) < deadzone:
        return 0
    return value

def moving_average(history):
    return sum(history) / len(history)

def process_joystick_input():
    global motorLeft, motorRight

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
    left_speed = (avg_forward + avg_steer) * SPEED_SCALE + left_trim
    right_speed = (avg_forward - avg_steer) * SPEED_SCALE + right_trim
    
    # Normalize motor speeds
    left_speed = max(min(left_speed, 63), -63)
    right_speed = max(min(right_speed, 63), -63)
    
    motorLeft = int(abs(left_speed)) & 63
    motorRight = int(abs(right_speed)) & 63
    
    if left_speed < 0:
        motorLeft |= 64  # Reverse bit for left motor
    else:
        motorLeft &= 63  # Forward for left motor
        
    if right_speed < 0:
        motorRight |= 192  # Reverse bit for right motor
    else:
        motorRight |= 128  # Forward for right motor
    
    logging.debug(f"Processed Left Motor: {motorLeft}, Processed Right Motor: {motorRight}")

def send_motor_command():
    packet = bytearray([motorRight, motorLeft])
    serialPort.write(packet)
    logging.debug(f"Sending command: L{motorLeft:02X} R{motorRight:02X}")

def main_loop():
    logging.info("Starting main loop. Move joystick to test.")
    try:
        while True:
            process_joystick_input()
            send_motor_command()
            time.sleep(0.05)  # Reduced delay to improve responsiveness
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
        # Send stop command to ensure motors are stopped
        serialPort.write(bytearray([128, 128]))  # Stop motors
        pass

if __name__ == "__main__":
    main_loop()
