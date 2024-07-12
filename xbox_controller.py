import pygame

class XboxController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def get_joystick(self):
        pygame.event.pump()
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        return {'x': x, 'y': y}
