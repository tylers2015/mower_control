# Mower Control System

This project implements a control system for a robotic mower using a Raspberry Pi, an MDDS30 motor driver, and an Xbox One controller.

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

1. Clone this repository or download the files to your Raspberry Pi.

2. Navigate to the project directory:

cd ~/motor_control


3. Create and activate a virtual environment:

python3 -m venv mower_control_env source mower_control_env/bin/activate


4. Install the required packages:

pip install -r requirements.txt


5. Install necessary system dependencies:

sudo apt-get update sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev


## Configuration

1. Pair your Xbox One controller with your Raspberry Pi via Bluetooth.

2. Connect the MDDS30 motor driver to your Raspberry Pi via USB.

3. Edit the `config.ini` file to adjust settings:
- Set the correct serial port (usually `/dev/ttyUSB0`)
- Adjust DEADZONE, SPEED_SCALE, and motor trim values as needed

## Usage

1. Activate the virtual environment:

source ~/mower_control_env/bin/activate


2. Run the control script:

python xbox_mdds30_control.py


3. Use the left stick on the Xbox controller to drive the mower:
- Up/Down for forward/reverse
- Left/Right for steering

4. Press Ctrl+C to stop the script.

## Troubleshooting

- If you encounter permission issues with the serial port, add your user to the `dialout` group:

sudo usermod -a -G dialout $USER

Log out and log back in for the changes to take effect.

- Make sure the Xbox controller is properly paired and connected before running the script.

- Check that the MDDS30 is properly connected and the correct port is specified in `config.ini`.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

