# Mower Control System

Code to control an automated mower using Raspberry Pi, GPS, and Xbox controller.

## Table of Contents
- [Introduction](#introduction)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)
- [About](#about)

## Introduction

This project implements a control system for a robotic mower using a Raspberry Pi, an MDDS30 motor driver, and an Xbox One controller. The system reads joystick inputs to control the speed and direction of two motors, and includes features such as joystick deadzone handling, moving average filters for smoothing joystick input, and a shutdown mechanism triggered by a specific joystick button.

## Hardware Requirements
- Raspberry Pi (any model with USB and Bluetooth)
- MDDS30 Motor Driver
- Xbox One Controller
- Robot chassis with two DC motors

## Software Requirements
- Python 3.7+
- pygame
- pyserial

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/tylers2015/mower_control.git
    cd mower_control
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv mower_control_env
    source mower_control_env/bin/activate
    ```

3. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Install necessary system dependencies**:
    ```bash
    sudo apt-get update
    sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev
    ```

## Configuration

1. **Pair your Xbox One controller with your Raspberry Pi via Bluetooth**.

2. **Connect the MDDS30 motor driver to your Raspberry Pi via USB**.

3. **Edit the `config.ini` file to adjust settings**:
    - Set the correct serial port (usually `/dev/ttyUSB0`)
    - Adjust `DEADZONE`, `SPEED_SCALE`, and motor trim values as needed

## Usage

1. **Activate the virtual environment**:
    ```bash
    source mower_control_env/bin/activate
    ```

2. **Run the control script**:
    ```bash
    python motor_control.py
    ```

3. **Use the left stick on the Xbox controller to drive the mower**:
    - Up/Down for forward/reverse
    - Left/Right for steering

4. **Press Ctrl+C to stop the script**.

## Command Reference

### Systemd Service Management
- **Start the service**:
    ```bash
    sudo systemctl start mower_control.service
    ```
- **Stop the service**:
    ```bash
    sudo systemctl stop mower_control.service
    ```
- **Restart the service**:
    ```bash
    sudo systemctl restart mower_control.service
    ```
- **View the service logs**:
    ```bash
    sudo journalctl -u mower_control.service -e
    ```

### Serial Port Configuration
- Configure the serial port in the `motor_control.py` script:
    ```python
    MOTOR_SERIAL_PORT = '/dev/ttyUSB0'
    BAUD_RATE = 9600
    ```

### Joystick Calibration
- Adjust joystick deadzone and trims:
    ```python
    DEADZONE = 0.1
    LEFT_TRIM = 0
    RIGHT_TRIM = 0
    ```

### Logging
- Logs are stored in `mower_control.log`:
    ```python
    logging.basicConfig(filename='mower_control.log', level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    ```

### Shutdown Mechanism
- Set the button index and hold time for shutdown:
    ```python
    VIEW_BUTTON = 10
    SHUTDOWN_HOLD_TIME = 3
    ```

## Troubleshooting

### Common Issues
- **No joystick detected**: Ensure the joystick is properly connected and recognized by the system.
- **Serial communication errors**: Check the serial port configuration and ensure the correct port is used.
- **Service fails to start**: Use `journalctl` to view detailed logs and identify issues.

### Logs
- Check the log file `mower_control.log` for detailed debug information:
    ```bash
    tail -f mower_control.log
    ```

- If you encounter permission issues with the serial port, add your user to the `dialout` group:
    ```bash
    sudo usermod -a -G dialout $USER
    ```
    Log out and log back in for the changes to take effect.

- Ensure the Xbox controller is properly paired and connected before running the script.
- Check that the MDDS30 is properly connected and the correct port is specified in `config.ini`.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## About

Code to control an automated mower using Raspberry Pi, GPS, and Xbox controller.

For more information, visit the [GitHub repository](https://github.com/tylers2015/mower_control).

