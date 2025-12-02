import pygame
pygame.init()

try:
    screen = pygame.display.set_mode((400, 400))
    print("SUCCESS: SDL created a window.")
except Exception as e:
    print("FAILED to create window:", e)

input("Press ENTER to exit...")
