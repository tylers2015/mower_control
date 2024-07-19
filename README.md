# Motor Control for Zero-Turn Mower

This project provides a Python script to control a zero-turn mower using an Xbox controller. The control scheme uses the left joystick for forward/backward movement and the right joystick for steering, allowing precise control of the mower's movements.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Raspberry Pi
- Python 3.7+
- Xbox Wireless Controller
- Cytron Motor Driver
- Pygame library
- PySerial library

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/zero-turn-mower-control.git
    cd zero-turn-mower-control
    ```

2. **Set Up a Virtual Environment**

    ```bash
    python3 -m venv mower_control_env
    source mower_control_env/bin/activate
    ```

3. **Install Dependencies**

    ```bash
    pip install pygame pyserial
    ```

## Usage

1. **Connect the Xbox Controller**

    Ensure your Xbox controller is connected to the Raspberry Pi via Bluetooth or USB.

2. **Connect the Motor Driver**

    Connect the Cytron Motor Driver to the Raspberry Pi's serial port (`/dev/ttyUSB0`).

3. **Run the Script**

    ```bash
    python mower_control.py
    ```

4. **Control the Mower**

    - **Left Joystick (Axis 0)**: Forward/Backward movement
    - **Right Joystick (Axis 1)**: Left/Right steering

## Configuration

### Adjusting Speed

The script includes a `SPEED_SCALE` variable to adjust the overall speed of the motors. You can modify this value to increase or decrease the speed.

    ```python
    SPEED_SCALE = 100  # Adjust this value as needed
    ```

### Motor Trim

If the motors do not run at the same speed, you can adjust the `left_trim` and `right_trim` variables to compensate.

    ```python
    left_trim = 0
    right_trim = 0
    ```

### Deadzone

The `DEADZONE` variable helps to handle joystick drift by ignoring small inputs.

    ```python
    DEADZONE = 0.1
    ```

## Troubleshooting

- **No response from the motors**: 
    - Ensure the serial port (`/dev/ttyUSB0`) is correct and the motor driver is properly connected.
    - Check the connections and power supply to the motor driver.
  
- **Joystick not detected**: 
    - Ensure the Xbox controller is properly connected and recognized by the Raspberry Pi.
    - Check the device path (`/dev/input/eventX`) in the script.

- **Motors not moving as expected**:
    - Verify the joystick axis assignments are correct.
    - Adjust the `SPEED_SCALE`, `left_trim`, and `right_trim` values to calibrate the motor speeds.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Example

Below is a sample of what the logging output might look like when running the script:

    ```plaintext
    DEBUG:root:Opened serial port /dev/ttyUSB0 at 9600 baud
    DEBUG:root:Found gamepad: Xbox Wireless Controller at /dev/input/event4
    DEBUG:root:Entering continuous control loop. Press Ctrl-C to exit.
    DEBUG:root:Raw Forward: 0.5, Raw Steer: -0.3
    DEBUG:root:Processed Left Motor: 128, Processed Right Motor: 76
    DEBUG:root:Sending command: L80 R4C
    ...
    ```

## Support

For any questions or support, please open an issue on the [GitHub repository](https://github.com/yourusername/zero-turn-mower-control/issues).
