import unittest
from unittest.mock import patch, MagicMock
import motor_control
import serial

class TestMotorControl(unittest.TestCase):

    @patch('motor_control.serial.Serial')
    def test_init_serial_success(self, mock_serial):
        mock_serial.return_value = MagicMock()
        result = motor_control.init_serial('/dev/ttyUSB0')
        self.assertIsNotNone(result)

    @patch('motor_control.serial.Serial')
    def test_init_serial_failure(self, mock_serial):
        mock_serial.side_effect = serial.SerialException("Error")
        result = motor_control.init_serial('/dev/ttyUSB0')
        self.assertIsNone(result)

    @patch('motor_control.gps_serial.readline')
    def test_update_gps_position(self, mock_readline):
        mock_readline.return_value = b'$GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47'
        motor_control.update_gps_position()
        self.assertNotEqual(motor_control.current_position, (0.0, 0.0))

    @patch('motor_control.motor_serial.write')
    def test_update_motor_control(self, mock_write):
        motor_control.update_motor_control(1.0, 1.0)
        mock_write.assert_called_with(b'L1.0R1.0\n')

    def test_load_grid(self):
        with patch('builtins.open', unittest.mock.mock_open(read_data='[[0, 1], [1, 0]]')):
            motor_control.load_grid('test_grid.json')
        self.assertEqual(motor_control.grid, [[0, 1], [1, 0]])

    def test_save_grid(self):
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            motor_control.save_grid('test_grid.json')
            mock_file().write.assert_called_once()

if __name__ == '__main__':
    unittest.main()
