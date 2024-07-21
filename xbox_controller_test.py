import pygame

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Get the number of joysticks
joystick_count = pygame.joystick.get_count()
print(f"Number of joysticks: {joystick_count}")

# Iterate through each joystick
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    print(f"Joystick {i}: {joystick.get_name()}")
    print(f"Number of axes: {joystick.get_numaxes()}")
    print(f"Number of buttons: {joystick.get_numbuttons()}")

# Quit Pygame
pygame.quit()
