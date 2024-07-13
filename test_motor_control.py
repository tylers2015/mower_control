import unittest
from unittest.mock import patch, MagicMock
import motor_control
import json

class TestMotorControl(unittest.TestCase):

    @patch('motor_control.serial.Serial')
    def test_init_serial_success(self, mock_serial):
        mock_serial.return_value = MagicMock()
        result = motor_control.init_serial('/dev/ttyUSB0')
        self.assertIsNotNone(result)
        mock_serial.assert_called_with('/dev/ttyUSB0', 9600, timeout=1)

    @patch('motor_control.serial.Serial')
    def test_init_serial_failure(self, mock_serial):
        mock_serial.side_effect = motor_control.serial.SerialException("Port not found")
        result = motor_control.init_serial('/dev/ttyUSB0')
        self.assertIsNone(result)
        mock_serial.assert_called_with('/dev/ttyUSB0', 9600, timeout=1)

    def test_load_grid_success(self):
        mock_grid = [[0, 1], [1, 0]]
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(mock_grid))):
            motor_control.load_grid('test_grid.json')
            self.assertEqual(motor_control.grid, mock_grid)

    def test_load_grid_failure(self):
        with patch('builtins.open', side_effect=Exception('File not found')):
            with self.assertLogs('motor_control', level='ERROR') as cm:
                motor_control.load_grid('test_grid.json')
            self.assertIn('ERROR:motor_control:Error loading grid file test_grid.json: File not found', cm.output)

    def test_save_grid_success(self):
        mock_grid = [[0, 1], [1, 0]]
        motor_control.grid = mock_grid
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            motor_control.save_grid('test_grid.json')
            mock_file().write.assert_called_once_with(json.dumps(mock_grid))

    def test_save_grid_failure(self):
        with patch('builtins.open', side_effect=Exception('Write error')):
            with self.assertLogs('motor_control', level='ERROR') as cm:
                motor_control.save_grid('test_grid.json')
            self.assertIn('ERROR:motor_control:Error saving grid file test_grid.json: Write error', cm.output)

if __name__ == '__main__':
    unittest.main()
