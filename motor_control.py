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
MOTOR_SERIAL_PORT = '/dev/ttyAMA1'  # Path for motor controller via UART
SERVO_ON = 7.5  # Duty cycle to turn on servo
SERVO_OFF = 0  # Duty cycle to turn off servo
EMERGENCY_STOP_BUTTON = 7  # Designated button for emergency stop (Xbox button)
LOG_FILE = 'gps_data.log'
GRID_SIZE = 100

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
gps_logger = logging.getLogger('GPSLogger')
gps_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE)
gps_logger.addHandler(file_handler)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# Initialize Pygame for Xbox controller
pygame.init()
pygame.joystick.init()

# Ensure at least one joystick is connected
if pygame.joystick.get_count() < 1:
    raise Exception("No joystick connected")

controller = pygame.joystick.Joystick(0)
controller.init()

# Initialize Serial for GPS and Motor controller
def init_serial(port: str, baudrate: int = 9600, timeout: int = 1) -> Optional[serial.Serial]:
    try:
        return serial.Serial(port, baudrate, timeout=timeout)
    except serial.SerialException as e:
        logging.error(f"Could not open serial port {port}: {e}")
        return None

gps_serial = init_serial(GPS_SERIAL_PORT)
motor_serial = init_serial(MOTOR_SERIAL_PORT)

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
            messagebox.showerror("Load Grid", f"Grid file {file_name} does not exist.")
    except Exception as e:
        logging.error(f"Error loading grid file {file_name}: {e}")
        messagebox.showerror("Load Grid", f"Error loading grid file {file_name}: {e}")

# Save grid data to file
def save_grid(file_name: str) -> None:
    try:
        with open(file_name, 'w') as file:
            json.dump(grid, file)
        logging.info(f"Grid data saved to {file_name}.")
    except Exception as e:
        logging.error(f"Error saving grid file {file_name}: {e}")
        messagebox.showerror("Save Grid", f"Error saving grid file {file_name}: {e}")

load_grid(current_grid_file)

# GUI setup
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
                if grid[y][x] == 1:  # Path
                    self.canvas.create_rectangle(x * 5, y * 5, (x + 1) * 5, (y + 1) * 5, fill="blue")
                elif grid[y][x] == -1:  # Obstacle
                    self.canvas.create_rectangle(x * 5, y * 5, (x + 1) * 5, (y + 1) * 5, fill="red")

    def update_gui(self) -> None:
        self.lat_label.config(text=f"Latitude: {current_position[0]:.6f}")
        self.lon_label.config(text=f"Longitude: {current_position[1]:.6f}")
        self.gps_status_label.config(text=f"GPS Status: {gps_status}")
        self.motor_status_label.config(text=f"Motor Status: {motor_status}")
        self.signal_quality_label.config(text=f"Signal Quality: {signal_quality}")
        self.mapping_mode_label.config(text=f"Mapping Mode: {'On' if mapping_mode else 'Off'}")
        self.obstacle_mode_label.config(text=f"Obstacle Mode: {'On' if obstacle_mode else 'Off'}")
        self.draw_grid()
        self.root.after(1000, self.update_gui)

    def save_grid(self) -> None:
        file_name = simpledialog.askstring("Save Grid", "Enter file name:")
        if file_name:
            save_grid(file_name + ".json")
            messagebox.showinfo("Save Grid", f"Grid data saved to {file_name}.json")

    def load_grid(self) -> None:
        file_name = simpledialog.askstring("Load Grid", "Enter file name:")
        if file_name:
            load_grid(file_name + ".json")
            messagebox.showinfo("Load Grid", f"Grid data loaded from {file_name}.json")

def start_gui() -> None:
    root = tk.Tk()
    app = GPSApp(root)
    root.mainloop()

gui_thread = Thread(target=start_gui)
gui_thread.start()

def update_motor_control(left_speed: float, right_speed: float) -> None:
    try:
        motor_serial.write(f'L{left_speed}R{right_speed}\n'.encode())
        logging.info(f'Motor control updated: L={left_speed}, R={right_speed}')
    except (serial.SerialException, AttributeError) as e:
        logging.error(f"Error sending motor control data: {e}")
        logging.error(traceback.format_exc())
        reconnect_motor()

def update_gps_position() -> None:
    global current_position, gps_status, signal_quality
    try:
        line = gps_serial.readline().decode('utf-8')
        if line.startswith('$GNGGA'):
            msg = pynmea2.parse(line)
            lat = msg.latitude
            lon = msg.longitude
            current_position = (lat, lon)
            signal_quality = msg.gps_qual
            gps_logger.info(f"{lat},{lon}")
            logging.info(f'GPS position updated: Latitude={lat}, Longitude={lon}')
            gps_status = "Connected"
    except (serial.SerialException, pynmea2.ParseError, AttributeError) as e:
        logging.error(f"Error reading GPS data: {e}")
        logging.error(traceback.format_exc())
        gps_status = "Disconnected"
        reconnect_gps()

def reconnect_gps() -> None:
    global gps_serial
    logging.info("Attempting to reconnect GPS...")
    gps_serial = init_serial(GPS_SERIAL_PORT)
    if gps_serial:
        gps_status = "Connected"
        logging.info("GPS reconnected successfully.")
    else:
        gps_status = "Disconnected"

def reconnect_motor() -> None:
    global motor_serial
    logging.info("Attempting to reconnect motor controller...")
    motor_serial = init_serial(MOTOR_SERIAL_PORT)
    if motor_serial:
        motor_status = "Connected"
        logging.info("Motor controller reconnected successfully.")
    else:
        motor_status = "Disconnected"

def handle_buttons() -> None:
    global mapping_mode, obstacle_mode, emergency_stop
    for event in pygame.event.get():
       