#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Define the motor control pins here
RIGHT_MOTOR_PIN = 17
LEFT_MOTOR_PIN = 18

def reset_motors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RIGHT_MOTOR_PIN, GPIO.OUT)
    GPIO.setup(LEFT_MOTOR_PIN, GPIO.OUT)

    # Set the motor pins to low to stop them
    GPIO.output(RIGHT_MOTOR_PIN, GPIO.LOW)
    GPIO.output(LEFT_MOTOR_PIN, GPIO.LOW)

    # Keep the pins low for a short duration to ensure they stop
    time.sleep(1)

    # Cleanup GPIO settings
    GPIO.cleanup()

if __name__ == "__main__":
    reset_motors()
