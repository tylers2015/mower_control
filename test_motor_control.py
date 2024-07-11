import unittest
from unittest.mock import MagicMock, patch
from motor_control import initialize_motor, update_motor_control, reconnect_motor

class TestMotorControl(unittest.TestCase):

    @patch('motor_control.serial.Serial')
    def test_initialize_motor(self, mock_serial):
        mock_serial.return_value = MagicMock()
        motor = initialize_motor()
        self.assertIsNotNone(motor, "Motor should be initialized")
        mock_serial.assert_called_with('/dev/ttyUSB1', baudrate=9600, timeout=1)

    @patch('motor_control.serial.Serial')
    def test_reconnect_motor(self, mock_serial):
        mock_serial.side_effect = [serial.SerialException, MagicMock()]
        motor = reconnect_motor()
        self.assertIsNotNone(motor, "Motor should be reconnected")
        self.assertEqual(mock_serial.call_count, 2)

    @patch('motor_control.serial.Serial')
    def test_update_motor_control(self, mock_serial):
        motor_serial = MagicMock()
        joystick_input = {'x': 0.5, 'y': -0.5}
        update_motor_control(motor_serial, joystick_input)
        command = "X:0.5 Y:-0.5"
        motor_serial.write.assert_called_with(command.encode())

if __name__ == '__main__':
    unittest.main()