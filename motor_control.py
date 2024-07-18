import pygame
import serial
import time
import logging

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Setup serial communication
serialPort = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

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

# Speed scaling factor to increase speed
SPEED_SCALE = 100  # Increase this value to increase speed

def process_joystick_input():
    global motorLeft, motorRight

    pygame.event.pump()
    
    forward = joystick.get_axis(0)  # Forward/backward control
    steer = joystick.get_axis(1)    # Left/right control
    
    logging.debug(f"Raw Forward: {forward}, Raw Steer: {steer}")
    
    if abs(forward) < DEADZONE:
        forward = 0
    if abs(steer) < DEADZONE:
        steer = 0
    
    # Calculate motor speeds for zero-turn steering with increased speed
    left_speed = (forward + steer) * SPEED_SCALE + left_trim
    right_speed = (forward - steer) * SPEED_SCALE + right_trim
    
    # Ensure values are within the 0-63 range and set direction bits
    motorLeft = int(left_speed) & 63
    motorRight = int(right_speed) & 63
    
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
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
        # Send stop command to ensure motors are stopped
        serialPort.write(bytearray([128, 128]))  # Stop motors
        pass

if __name__ == "__main__":
    main_loop()
