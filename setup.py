import pygame
import math
import random
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1920/2, 1080/2
dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)
center = pygame.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

pygame.display.set_caption("Basketball")
# icon = pygame.image.load("logo.ico")
# icon = pygame.transform.scale(icon, (32, 32))
# pygame.display.set_icon(icon)

clock = pygame.time.Clock()
fps = 120


class Colour:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (127, 127, 127)
    DARK_GRAY = (40, 40, 40)
    LIGHT_GRAY = (200,200,200)
    RED = (204, 0, 0)
    BLUE = (100, 149, 237)
    ORANGE = (244, 187, 68)
    TAN = (242, 210, 189)
