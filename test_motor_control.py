import pygame
import RPi.GPIO as GPIO
import time

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

# Set up GPIO
GPIO.setmode(GPIO.BCM)
motor_pin = 18
GPIO.setup(motor_pin, GPIO.OUT)
motor = GPIO.PWM(motor_pin, 100)
motor.start(0)

# Function to map joystick values to PWM duty cycle
def map_joystick_to_pwm(value):
    return (value + 1) * 50  # Convert -1 to 1 range to 0 to 100 duty cycle

# Check for joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    pygame.quit()
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Joystick detected:", joystick.get_name())

try:
    while True:
        pygame.event.pump()

        # Get the axis value (assuming single-axis control for simplicity)
        axis_value = joystick.get_axis(1)  # Left stick vertical axis
        pwm_value = map_joystick_to_pwm(axis_value)
        motor.ChangeDutyCycle(pwm_value)

        print(f"Axis Value: {axis_value}, PWM Duty Cycle: {pwm_value}")

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    motor.stop()
    GPIO.cleanup()
    pygame.quit()
