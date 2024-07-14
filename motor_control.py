import pygame
import serial
import RPi.GPIO as GPIO
import time
import logging
import pynmea2
import tkinter as tk
from tkinter import simpledialog, messagebox
from threading import Thread
import traceback
import json
import os
from typing import Tuple, List, Optional

# Constants
SERVO_PIN = 18
BACKUP_DISTANCE = 2  # feet
GPS_SERIAL_PORT = '/dev/ttyUSB0'  # Path for corrected GPS data
MOTOR_SERIAL_PORT = '/dev/ttyUSB0'  # Path for motor controller via UART
SERVO_ON = 7.5  # Duty cycle to turn on servo
SERVO_OFF = 0  # Duty cycle to turn off servo
EMERGENCY_STOP_BUTTON = 4  # Designated button for emergency stop
LOG_FILE = 'gps_data.log'
GRID_SIZE = 100

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
gps_logger = logging.getLogger('GPSLogger')
motor_logger = logging.getLogger('MotorLogger')

# Initialize log file handlers
gps_file_handler = logging.FileHandler(LOG_FILE)
gps_logger.addHandler(gps_file_handler)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# Initialize Pygame for Xbox controller
pygame.init()
pygame.joystick.init()
try:
    controller = pygame.joystick.Joystick(0)
    controller.init()
except pygame.error:
    logging.error("No joystick found.")
    controller = None

# Initialize Serial for GPS and Motor controller
def init_serial(port: str, baudrate: int = 9600, timeout: int = 1) -> Optional[serial.Serial]:
    try:
        return serial.Serial(port, baudrate, timeout=timeout)
    except serial.SerialException as e:
        logging.error(f"Could not open serial port {port}: {e}")
        return None

gps_serial = init_serial(GPS_SERIAL_PORT)
motor_serial = init_serial(MOTOR_SERIAL_PORT)

if not gps_serial:
    logging.error("GPS serial port could not be initialized.")
if not motor_serial:
    logging.error("Motor serial port could not be initialized.")

# Mapping variables
mapping_mode = False
obstacle_mode = False
current_position: Tuple[float, float] = (0.0, 0.0)
grid: List[List[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
emergency_stop = False
gps_status = "Disconnected"
motor_status = "Disconnected"
signal_quality = 0
current_grid_file = 'default_grid.json'

# Load grid data from file
def load_grid(file_name: str) -> None:
    global grid, current_grid_file
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                grid = json.load(file)
            logging.info(f"Grid data loaded from {file_name}.")
            current_grid_file = file_name
        else:
            logging.error(f"Grid file {file_name} does not exist.")
            if 'DISPLAY' in os.environ:
                messagebox.showerror("Load Grid", f"Grid file {file_name} does not exist.")
    except Exception as e:
        logging.error(f"Error loading grid file {file_name}: {e}")
        if 'DISPLAY' in os.environ:
            messagebox.showerror("Load Grid", f"Error loading grid file {file_name}: {e}")

# Save grid data to file
def save_grid(file_name: str) -> None:
    try:
        with open(file_name, 'w') as file:
            json.dump(grid, file)
        logging.info(f"Grid data saved to {file_name}.")
    except Exception as e:
        logging.error(f"Error saving grid file {file_name}: {e}")
        if 'DISPLAY' in os.environ:
            messagebox.showerror("Save Grid", f"Error saving grid file {file_name}: {e}")

load_grid(current_grid_file)

# GUI setup
if 'DISPLAY' in os.environ:
    class GPSApp:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("GPS Monitor")
            self.lat_label = tk.Label(root, text="Latitude: 0.0")
            self.lat_label.pack()
            self.lon_label = tk.Label(root, text="Longitude: 0.0")
            self.lon_label.pack()
            self.gps_status_label = tk.Label(root, text="GPS Status: Disconnected")
            self.gps_status_label.pack()
            self.motor_status_label = tk.Label(root, text="Motor Status: Disconnected")
            self.motor_status_label.pack()
            self.signal_quality_label = tk.Label(root, text="Signal Quality: 0")
            self.signal_quality_label.pack()
            self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
            self.canvas.pack()
            self.save_button = tk.Button(root, text="Save Grid", command=self.save_grid)
            self.save_button.pack()
            self.load_button = tk.Button(root, text="Load Grid", command=self.load_grid)
            self.load_button.pack()
            self.mapping_mode_label = tk.Label(root, text="Mapping Mode: Off")
            self.mapping_mode_label.pack()
            self.obstacle_mode_label = tk.Label(root, text="Obstacle Mode: Off")
            self.obstacle_mode_label.pack()
            self.legend = tk.Label(root, text="Legend:\nBlue: Path\nRed: Obstacle")
            self.legend.pack()
            self.update_gui()

        def draw_grid(self) -> None:
            self.canvas.delete("all")
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    color = "white"
                    if grid[y][x] == 1:  # Path
                        color = "blue"
                    elif grid[y][x] == 2:  # Obstacle
                        color = "red"
                    self.canvas.create_rectangle(x*5, y*5, x*5+5, y*5+5, fill=color, outline="black")

        def update_gui(self) -> None:
            self.lat_label.config(text=f"Latitude: {current_position[0]}")
            self.lon_label.config(text=f"Longitude: {current_position[1]}")
            self.gps_status_label.config(text=f"GPS Status: {gps_status}")
            self.motor_status_label.config(text=f"Motor Status: {motor_status}")
            self.signal_quality_label.config(text=f"Signal Quality: {signal_quality}")
            self.mapping_mode_label.config(text=f"Mapping Mode: {'On' if mapping_mode else 'Off'}")
            self.obstacle_mode_label.config(text=f"Obstacle Mode: {'On' if obstacle_mode else 'Off'}")
            self.draw_grid()
            self.root.after(1000, self.update_gui)  # Refresh every second

        def save_grid(self) -> None:
            file_name = simpledialog.askstring("Save Grid", "Enter file name:")
            if file_name:
                save_grid(file_name)

        def load_grid(self) -> None:
            file_name = simpledialog.askstring("Load Grid", "Enter file name:")
            if file_name:
                load_grid(file_name)

    root = tk.Tk()
    app = GPSApp(root)
    root.mainloop()
else:
    root = None

# Dead zone function to ignore small joystick movements
def apply_dead_zone(value: float, dead_zone: float = 0.2) -> float:  # Increased dead zone to 0.2
    """Apply a dead zone to the joystick input to ignore small movements."""
    if abs(value) < dead_zone:
        return 0
    return value

# Ensure values are within -1 to 1 range
def clamp(value: float, min_value: float = -1.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))

# Main loop
def main_loop() -> None:
    global current_position, gps_status, motor_status, signal_quality, emergency_stop
    try:
        while True:
            pygame.event.pump()
            if controller and controller.get_button(EMERGENCY_STOP_BUTTON):
                emergency_stop = True
                motor_status = "Emergency Stop"
                servo.ChangeDutyCycle(SERVO_OFF)
                logging.info("Emergency Stop Activated")
                motor_serial.write("STOP\n".encode())
                continue
            emergency_stop = False
            motor_status = "Running"
            # Update motor control
            if controller:
                raw_left_stick_y = controller.get_axis(1)
                raw_right_stick_y = controller.get_axis(3)
                left_stick_y = apply_dead_zone(raw_left_stick_y)
                right_stick_y = apply_dead_zone(raw_right_stick_y)
                left_stick_y = clamp(left_stick_y)
                right_stick_y = clamp(right_stick_y)
                logging.debug(f"Raw Left Stick Y: {raw_left_stick_y}, Raw Right Stick Y: {raw_right_stick_y}")
                logging.debug(f"Processed Left Stick Y: {left_stick_y}, Processed Right Stick Y: {right_stick_y}")

                if left_stick_y == 0 and right_stick_y == 0:
                    motor_command = "STOP\n"
                else:
                    motor_command = f"L{left_stick_y:.2f}R{right_stick_y:.2f}\n"

                logging.debug(f"Motor Command: {motor_command}")
                motor_serial.write(motor_command.encode())
            else:
                logging.debug("No controller connected.")
            # Read GPS data
            if gps_serial and gps_serial.in_waiting > 0:
                line = gps_serial.readline().decode('ascii', errors='replace')
                if line.startswith('$GPGGA'):
                    msg = pynmea2.parse(line)
                    current_position = (msg.latitude, msg.longitude)
                    signal_quality = msg.gps_qual
                    gps_status = "Connected"
                    logging.debug(f"GPS Position: {current_position}, Signal Quality: {signal_quality}")
            else:
                logging.debug("No GPS data available.")
            time.sleep(0.1)
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
        logging.error(traceback.format_exc())

thread = Thread(target=main_loop)
thread.daemon = True
thread.start()

if root:
    root.mainloop()
