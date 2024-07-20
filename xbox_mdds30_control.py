import pygame
import serial
import time
import logging
import configparser
import os

# Read configuration
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_file_path)

DEADZONE = float(config['MOTOR_CONTROL']['DEADZONE'])
SPEED_SCALE = int(config['MOTOR_CONTROL']['SPEED_SCALE'])
left_trim = int(config['MOTOR_CONTROL']['LEFT_TRIM'])
right_trim = int(config['MOTOR_CONTROL']['RIGHT_TRIM'])
SERIAL_PORT = config['SERIAL']['PORT']
BAUD_RATE = int(config['SERIAL']['BAUD_RATE'])

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Setup serial communication for MDDS30
serialPort = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

def setup_joystick():
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        logging.info("Xbox One controller initialized successfully.")
        return joystick
    except pygame.error as e:
        logging.error(f"Xbox One controller initialization failed: {e}")
        return None

def process_joystick_input(joystick):
    global motorLeft, motorRight

    pygame.event.pump()
    
    forward = joystick.get_axis(1)  # Left stick Y-axis (forward/backward)
    steer = joystick.get_axis(0)    # Left stick X-axis (left/right)
    
    logging.debug(f"Raw Forward: {forward}, Raw Steer: {steer}")
    
    if abs(forward) < DEADZONE:
        forward = 0
    if abs(steer) < DEADZONE:
        steer = 0
    
    # Invert forward axis as Xbox controller Y-axis is inverted
    forward = -forward
    
    # Calculate motor speeds for differential steering
    left_speed = (forward + steer) * SPEED_SCALE + left_trim
    right_speed = (forward - steer) * SPEED_SCALE + right_trim
    
    # MDDS30 expects values between 0 and 255
    motorLeft = max(0, min(255, int(127 + left_speed)))
    motorRight = max(0, min(255, int(127 + right_speed)))
    
    logging.debug(f"Processed Left Motor: {motorLeft}, Processed Right Motor: {motorRight}")

def send_motor_command(serialPort):
    packet = bytearray([0x80, motorLeft, motorRight])
    try:
        serialPort.write(packet)
        logging.debug(f"Sending command: L{motorLeft:02X} R{motorRight:02X}")
    except serial.SerialException as e:
        logging.error(f"Serial communication error: {e}")

def main():
    joystick = setup_joystick()
    if not joystick:
        return

    logging.info("Starting main loop. Move left stick to control the robot.")
    try:
        while True:
            process_joystick_input(joystick)
            send_motor_command(serialPort)
            time.sleep(0.05)  # 50ms delay to avoid flooding the MDDS30
    except KeyboardInterrupt:
        logging.info("Exiting main loop.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Stop motors and clean up
        serialPort.write(bytearray([0x80, 127, 127]))
        serialPort.close()
        pygame.quit()

if __name__ == "__main__":
    main()

