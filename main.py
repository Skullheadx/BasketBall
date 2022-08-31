from setup import *
from game import Game

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
delta = 1000/fps
is_running = True

scene = Game()

while is_running:
    if pygame.event.peek(pygame.QUIT):
        is_running = False

    scene.update(delta)
    scene.draw(screen)

    pygame.display.update()
    delta = clock.tick(fps)

pygame.quit()
