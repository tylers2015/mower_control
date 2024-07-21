# File: kill_switch_control.py

import pygame
import logging
import time
import RPi.GPIO as GPIO

# Initialize Pygame (only required if this module is used independently)
pygame.init()
pygame.joystick.init()

# GPIO setup
KILL_SWITCH_PIN = 18  # Replace with your desired GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(KILL_SWITCH_PIN, GPIO.OUT)

# Setup PWM on the GPIO pin
pwm = GPIO.PWM(KILL_SWITCH_PIN, 50)  # 50 Hz frequency
pwm.start(0)

# Joystick button index for the kill switch (B button)
KILL_SWITCH_BUTTON = 1

# Current state of the kill switch
kill_switch_state = False
last_button_state = False

def initialize_joystick():
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick

joystick = initialize_joystick()

def set_servo_position(duty_cycle: float) -> None:
    pwm.ChangeDutyCycle(duty_cycle)
    logging.debug(f"Setting servo duty cycle: {duty_cycle}")

def toggle_kill_switch():
    global kill_switch_state
    kill_switch_state = not kill_switch_state
    duty_cycle = 12.5 if kill_switch_state else 2.5  # Adjust these values as needed for your servo
    set_servo_position(duty_cycle)
    logging.info(f"Kill switch {'ON' if kill_switch_state else 'OFF'}")

def process_kill_switch_input() -> None:
    global last_button_state
    pygame.event.pump()
    button_state = joystick.get_button(KILL_SWITCH_BUTTON)
    
    if button_state and not last_button_state:
        toggle_kill_switch()
        time.sleep(0.1)  # Adjusted debounce delay
    
    last_button_state = button_state

if __name__ == "__main__":
    try:
        while True:
            process_kill_switch_input()
            time.sleep(0.05)  # Adjust delay as needed
    except KeyboardInterrupt:
        logging.info("Exiting kill switch control.")
        pwm.stop()
        GPIO.cleanup()
        pass
