# File: kill_switch_control.py

import pygame
import serial
import logging

# Initialize Pygame (only required if this module is used independently)
pygame.init()
pygame.joystick.init()

# Setup serial communication for the servo (assuming a different port for the servo)
servo_serial_port = serial.Serial("/dev/ttyUSB1", 9600, timeout=0.5)

# Servo positions
SERVO_ON_POSITION = 180
SERVO_OFF_POSITION = 0

# Joystick button index for the kill switch (B button)
KILL_SWITCH_BUTTON = 1

# Current state of the kill switch
kill_switch_state = False

def initialize_joystick():
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick

joystick = initialize_joystick()

def set_servo_position(position: int) -> None:
    # Send the position command to the servo
    packet = bytearray([position])
    servo_serial_port.write(packet)
    logging.debug(f"Setting servo position: {position}")

def toggle_kill_switch():
    global kill_switch_state
    kill_switch_state = not kill_switch_state
    position = SERVO_ON_POSITION if kill_switch_state else SERVO_OFF_POSITION
    set_servo_position(position)
    logging.info(f"Kill switch {'ON' if kill_switch_state else 'OFF'}")

def process_kill_switch_input() -> None:
    pygame.event.pump()
    if joystick.get_button(KILL_SWITCH_BUTTON):
        toggle_kill_switch()
        # Add a short delay to debounce the button press
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        while True:
            process_kill_switch_input()
            time.sleep(0.05)  # Adjust delay as needed
    except KeyboardInterrupt:
        logging.info("Exiting kill switch control.")
        pass
