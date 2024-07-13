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

    Install Required Packages:

    sh

    sudo apt-get update
    sudo apt-get install python3-pygame python3-rpi.gpio bluetooth bluez blueman

Running the Script

    Execute the Script:

    sh

    python3 src/mower_control.py

    Observe the Console and GUI:
        Confirm that the motors respond to controller inputs and the GPS data is being updated correctly.

Troubleshooting

    Connection Issues:
        Ensure the Xbox controller is in pairing mode.
        Verify that the Raspberry Pi’s Bluetooth is active and functional.
        Restart the Bluetooth service if needed:

        sh

        sudo systemctl restart bluetooth

Connecting the Xbox One Controller via Bluetooth

    Turn on the Xbox One Controller:
        Press the Xbox button to turn it on.
        Put it in pairing mode by holding the sync button until the Xbox button flashes rapidly.

    Pair the Controller with Raspberry Pi:
        Open a terminal and use the bluetoothctl tool:

        sh

bluetoothctl

In the bluetoothctl prompt, enter the following commands:

sh

agent on
default-agent
scan on

Wait for the controller to appear in the list, then note its MAC address. Pair with it using:

sh

        pair <MAC_ADDRESS>
        trust <MAC_ADDRESS>
        connect <MAC_ADDRESS>

    Verify the Connection:
        Ensure that the controller is connected. You should see confirmation messages indicating a successful connection.

Setting Up SSH Key for GitHub

    Generate SSH Key:

    sh

ssh-keygen -t ed25519 -C "your_email@example.com"

Follow the prompts to save the key (press Enter to accept the default location) and set a passphrase if desired.

Add Your SSH Key to the ssh-agent:

sh

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

Copy Your SSH Key to the Clipboard:

sh

cat ~/.ssh/id_ed25519.pub

Copy the output of this command.

Add the SSH Key to Your GitHub Account:

    Go to GitHub SSH keys settings.
    Click "New SSH key".
    Paste the copied SSH key into the "Key" field.
    Add a descriptive title.
    Click "Add SSH key".

Change the Remote URL to Use SSH:

sh

git remote set-url origin git@github.com:tylers2015/mower_control.git

Push the test Branch to the Remote Repository:

sh

    git push origin test

License

This project is licensed under the MIT License. For further details, please refer to the complete documentation and code in the repository.

rust


This README file now includes the steps for setting up the SSH key for GitHub.

