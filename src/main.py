import pygame
from game import Game

def main():
    pygame.init()
    game = Game(name='Chess',
                window_height=800,
                window_width=800,
                bot_depth=3)
    game.run()
    pygame.quit()

if __name__ == '__main__':
    main()