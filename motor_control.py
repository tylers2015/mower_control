import time
import logging
import pygame
import serial

pygame.init()
pygame.joystick.init()

logging.basicConfig(level=logging.DEBUG)

if pygame.joystick.get_count() < 1:
    raise Exception("No joystick found")
    
joystick = pygame.joystick.Joystick(0)
joystick.init()

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
except Exception as e:
    logging.error(f"Error opening serial port {SERIAL_PORT}: {e}")
    raise

DEADZONE = 0.1

def process_input(raw_value):
    if abs(raw_value) < DEADZONE:
        return 0
    return raw_value

def send_motor_command(left_speed, right_speed):
    command = f'L{left_speed:.2f}R{right_speed:.2f}\n'
    logging.debug(f"Sending command: {command.strip()}")
    ser.write(command.encode())

def main_loop():
    try:
        while True:
            pygame.event.pump()
            raw_left_stick_y = joystick.get_axis(1)
            raw_right_stick_y = joystick.get_axis(3)
            logging.debug(f"Raw Left Stick Y: {raw_left_stick_y}, Raw Right Stick Y: {raw_right_stick_y}")

            processed_left_stick_y = process_input(raw_left_stick_y)
            processed_right_stick_y = process_input(raw_right_stick_y)
            logging.debug(f"Processed Left Stick Y: {processed_left_stick_y}, Processed Right Stick Y: {processed_right_stick_y}")

            if processed_left_stick_y == 0 and processed_right_stick_y == 0:
                send_motor_command(0, 0)
            else:
                send_motor_command(processed_left_stick_y, processed_right_stick_y)

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        ser.close()

if __name__ == "__main__":
    logging.info("Starting main loop. Move joystick to test.")
    main_loop()