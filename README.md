# Mower Control

Code to control an automated mower using Raspberry Pi, GPS, and Xbox controller.

## Project Overview

This project focuses on developing an autonomous lawn mower controlled using an Xbox One controller. The system integrates GPS data handling, motor control, and a graphical user interface (GUI) for monitoring and controlling the mower.

### Main Components and Functionalities

1. **Libraries and Constants**:
   - Libraries: 
     - `pygame`: For Xbox controller input handling.
     - `serial`: For serial communication with GPS and motor controller.
     - `RPi.GPIO`: For controlling GPIO pins on the Raspberry Pi.
     - Standard Python libraries: `time`, `logging`, `traceback`, `json`, `os`, `threading`, `tkinter`, `simpledialog`, `messagebox`.
     - `pynmea2`: For parsing GPS data.
   - Constants:
     - `SERVO_PIN`: GPIO pin for servo control.
     - `BACKUP_DISTANCE`: Distance to move backward in feet.
     - `GPS_SERIAL_PORT`: Serial port for GPS data.
     - `MOTOR_SERIAL_PORT`: Serial port for motor controller.
     - `SERVO_ON`: Duty cycle to turn on the servo.
     - `SERVO_OFF`: Duty cycle to turn off the servo.
     - `EMERGENCY_STOP_BUTTON`: Xbox controller button for emergency stop.
     - `LOG_FILE`: Log file for GPS data.
     - `GRID_SIZE`: Size of the grid for mapping.

2. **Logging Setup**:
   - Records GPS data and debug information to a log file (`gps_data.log`).

3. **GPIO Initialization**:
   - Sets up GPIO pins and PWM signal for the servo motor control.

4. **Xbox Controller Initialization**:
   - Uses `pygame` to initialize the Xbox controller and handle its inputs.

5. **Serial Port Initialization**:
   - Functions (`init_serial`) to initialize serial connections for the GPS and motor controller.

6. **Mapping and State Variables**:
   - Variables for mapping mode, obstacle mode, current GPS position, and a grid representing the mapped area.
   - The grid is a 2D list representing the lawn, with each cell indicating a path or obstacle.

7. **Grid Data Management**:
   - Functions to load (`load_grid`) and save (`save_grid`) grid data from/to a JSON file.

8. **GUI Setup**:
   - A `tkinter` based GUI displays GPS coordinates, motor status, signal quality, and interacts with the grid data.
   - Includes labels for displaying information, a canvas for the grid, and buttons for saving and loading the grid.

9. **Motor Control**:
   - Functions to update motor control based on joystick inputs and handle emergency stops.

10. **GPS Data Handling**:
   - Functions to read and parse GPS data from the serial port and update the current position and signal quality.

11. **Main Loop**:
   - Continuously checks for controller inputs, updates motor control, reads GPS data, and updates the GUI.

## Setup

### Prerequisites

- Raspberry Pi with Raspbian OS installed.
- Xbox One controller.
- GPS module.
- Motor controller and motors.
- Python 3 installed on the Raspberry Pi.

### Installation

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/tylers2015/mower_control.git
   cd mower_control
