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
motorDirection = False

# Calibration threshold to handle joystick drift
DEADZONE = 0.1

def process_joystick_input():
    global motorLeft, motorRight, motorDirection

    pygame.event.pump()
    
    right_stick_y = joystick.get_axis(1)
    left_stick_y = joystick.get_axis(4)
    
    logging.debug(f"Raw Left Stick Y: {left_stick_y}, Raw Right Stick Y: {right_stick_y}")
    
    if abs(left_stick_y) < DEADZONE:
        left_stick_y = 0
    if abs(right_stick_y) < DEADZONE:
        right_stick_y = 0
    
    motorLeft = int(left_stick_y * 63)
    motorRight = int(right_stick_y * 63) | 128
    
    if motorLeft < 0:
        motorLeft = (abs(motorLeft) & 63) | 64
    else:
        motorLeft &= 63
        
    if motorRight < 0:
        motorRight = (abs(motorRight) & 63) | 192
    else:
        motorRight &= 63
    
    logging.debug(f"Processed Left Stick Y: {motorLeft}, Processed Right Stick Y: {motorRight}")

def send_motor_command():
    packet = bytearray([motorRight, motorLeft])
    serialPort.write(packet)
    logging.debug(f"Sending command: R{motorRight:02X}L{motorLeft:02X}")

def main_loop():
    logging.info("Starting main loop. Move joystick to test.")
    try:
        while True:
            process_joystick_input()
            send_motor_command()
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
        pass

if __name__ == "__main__":
    main_loop()