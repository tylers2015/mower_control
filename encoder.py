import RPi.GPIO as GPIO
import time

# Pin definitions
ENCODER_LEFT_PIN = 17  # Replace with your actual GPIO pin
ENCODER_RIGHT_PIN = 27  # Replace with your actual GPIO pin

# Variables to store the encoder counts
left_encoder_count = 0
right_encoder_count = 0

# Encoder pulse callback
def left_encoder_callback(channel):
    global left_encoder_count
    left_encoder_count += 1

def right_encoder_callback(channel):
    global right_encoder_count
    right_encoder_count += 1

def setup():
    # Set up GPIO mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENCODER_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event detection for encoder pulses
    GPIO.add_event_detect(ENCODER_LEFT_PIN, GPIO.RISING, callback=left_encoder_callback)
    GPIO.add_event_detect(ENCODER_RIGHT_PIN, GPIO.RISING, callback=right_encoder_callback)

def calculate_distance(encoder_ticks, wheel_diameter, ticks_per_revolution):
    """ Calculate the distance traveled by the wheel """
    # Circumference of the wheel (C = π * d)
    wheel_circumference = 3.14159 * wheel_diameter
    # Distance traveled (d = (ticks / ticks_per_revolution) * circumference)
    distance = (encoder_ticks / ticks_per_revolution) * wheel_circumference
    return distance

if __name__ == "__main__":
    setup()
    
    try:
        wheel_diameter = 0.3  # Example wheel diameter in meters
        ticks_per_revolution = 360  # Example encoder ticks per revolution

        while True:
            # Print encoder counts and distances every second
            time.sleep(1)
            left_distance = calculate_distance(left_encoder_count, wheel_diameter, ticks_per_revolution)
            right_distance = calculate_distance(right_encoder_count, wheel_diameter, ticks_per_revolution)
            
            print(f"Left Motor - Ticks: {left_encoder_count}, Distance: {left_distance} m")
            print(f"Right Motor - Ticks: {right_encoder_count}, Distance: {right_distance} m")
            
            # Reset counts if needed or log data
            left_encoder_count = 0
            right_encoder_count = 0

    except KeyboardInterrupt:
        GPIO.cleanup()  # Clean up GPIO pins on exit