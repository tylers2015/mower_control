import unittest
from unittest.mock import patch, MagicMock
import serial
import RPi.GPIO as GPIO
import pygame
import json
import os

# Assuming your script is named `mower_control.py`
from mower_control import (
    SERVO_PIN, init_serial, load_grid, save_grid, update_motor_control,
    update_gps_position, reconnect_gps, reconnect_motor, handle_buttons,
    GRID_SIZE, GPS_SERIAL_PORT, MOTOR_SERIAL_PORT, gps_serial, motor_serial,
    current_position
)

class TestLawnMower(unittest.TestCase):

    @patch('mower_control.GPIO.setup')
    @patch('mower_control.GPIO.PWM')
    def test_gpio_initialization(self, mock_pwm, mock_setup):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)
        servo.start(0)

        mock_setup.assert_called_with(SERVO_PIN, GPIO.OUT)
        mock_pwm.assert_called_with(SERVO_PIN, 50)

    @patch('mower_control.pygame.joystick.Joystick')
    @patch('mower_control.pygame.joystick.get_count')
    def test_xbox_controller_initialization(self, mock_get_count, mock_joystick):
        mock_get_count.return_value = 1
        pygame.init()
        pygame.joystick.init()
        
        controller = pygame.joystick.Joystick(0)
        controller.init()

        mock_get_count.assert_called_once()
        mock_joystick.assert_called_with(0)
        controller.init.assert_called_once()

    @patch('mower_control.serial.Serial')
    def test_serial_initialization(self, mock_serial):
        mock_serial.return_value = MagicMock(spec=serial.Serial)
        gps_serial = init_serial(GPS_SERIAL_PORT)
        motor_serial = init_serial(MOTOR_SERIAL_PORT)

        mock_serial.assert_any_call(GPS_SERIAL_PORT, 9600, timeout=1)
        mock_serial.assert_any_call(MOTOR_SERIAL_PORT, 9600, timeout=1)
        self.assertIsInstance(gps_serial, serial.Serial)
        self.assertIsInstance(motor_serial, serial.Serial)

    @patch('builtins.open')
    @patch('os.path.exists')
    def test_load_grid(self, mock_exists, mock_open):
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps([[0] * GRID_SIZE] * GRID_SIZE)

        load_grid('test_grid.json')
        mock_open.assert_called_with('test_grid.json', 'r')

    @patch('builtins.open')
    def test_save_grid(self, mock_open):
        mock_open.return_value.__enter__.return_value = MagicMock()
        save_grid('test_grid.json')

        mock_open.assert_called_with('test_grid.json', 'w')
        mock_open.return_value.__enter__.return_value.write.assert_called_once()

    @patch('mower_control.motor_serial.write')
    def test_update_motor_control(self, mock_write):
        update_motor_control(0.5, 0.5)
        mock_write.assert_called_with(b'L0.5R0.5\n')

    @patch('mower_control.gps_serial.readline')
    @patch('mower_control.pynmea2.parse')
    def test_update_gps_position(self, mock_parse, mock_readline):
        mock_readline.return_value = b'$GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\n'
        mock_parse.return_value = MagicMock(latitude=48.1173, longitude=11.5167, gps_qual=1)

        update_gps_position()
        self.assertEqual(current_position, (48.1173, 11.5167))

    @patch('mower_control.init_serial')
    def test_reconnect_gps(self, mock_init_serial):
        mock_init_serial.return_value = MagicMock(spec=serial.Serial)
        reconnect_gps()
        mock_init_serial.assert_called_with(GPS_SERIAL_PORT)

    @patch('mower_control.init_serial')
    def test_reconnect_motor(self, mock_init_serial):
        mock_init_serial.return_value = MagicMock(spec=serial.Serial)
        reconnect_motor()
        mock_init_serial.assert_called_with(MOTOR_SERIAL_PORT)

    @patch('mower_control.pygame.event.get')
    @patch('mower_control.update_motor_control')
    def test_handle_buttons(self, mock_update_motor_control, mock_event_get):
        event = MagicMock()
        event.type = pygame.JOYBUTTONDOWN
        event.button = 7  # Emergency stop button
        mock_event_get.return_value = [event]

        handle_buttons()
        mock_update_motor_control.assert_called_with(0, 0)

if __name__ == '__main__':
    unittest.main()