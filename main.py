import pygame
import sqlite3
from src.game import Game
from src.db.database import ChessDatabase  # Подключаем класс базы данных

r'''
/ ============================ 

        CHESS GAME LAUNCHER

\ ============================ /
'''

def main():
    pygame.init()
    
    # Подключение к базе данных
    db_path = "data/openings/chess_openings.db"
    chess_db = ChessDatabase(db_path)

    # Получение размеров экрана
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w - 150
    screen_height = screen_info.current_h - 150
    
    # Установка размеров окна по меньшей из координат
    window_size = min(screen_width, screen_height)
    
    # Создание и запуск игры
    game = Game(window_height=window_size,
                window_width=window_size,
                isBotOn=True,
                bot_depth=3,
                chess_db=chess_db  # Передаем базу данных в игру
                )
    game.run()
    
    # Закрытие базы данных
    chess_db.close()
    pygame.quit()

if __name__ == '__main__':
    main()
