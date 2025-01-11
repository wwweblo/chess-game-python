import pygame
from src.game import Game
from src.db.new.database import ChessDatabase

r'''
/ ============================ 

        CHESS GAME LAUNCHER

\ ============================ /
'''

def getWindowSize():
    """Получение размеров экрана."""
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w - 150
    screen_height = screen_info.current_h - 150 
    window_size = min(screen_width, screen_height)
    return window_size

def loadSettings(file_path):
    """Загрузка настроек из текстового файла."""
    settings = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    # Автоматическое приведение типов
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    elif value.isdigit():
                        value = int(value)
                    settings[key] = value
    except FileNotFoundError:
        print(f"Settings file not found: {file_path}. Using default settings.")
    return settings

def main():
    pygame.init()

    # Загрузка настроек
    settings = loadSettings("user_settings.txt")

    # Подключение к базе данных
    db_path = settings.get("db_path", "data/openings/chess_openings.db")
    chess_db = ChessDatabase(db_path)
    
    # Определение размеров окна
    if settings.get("window_autosize", True):  # Если авторазмер включен
        window_size = getWindowSize()
        window_width = window_size
        window_height = window_size
    else:  # Используем размеры из настроек
        window_width = settings.get("window_width", 800)
        window_height = settings.get("window_height", 800)
    
    # Создание и запуск игры
    game = Game(
        # Размер окна
        window_height=window_height,
        window_width=window_width,

        # Настройки бота
        isBotOn=settings.get("isBotOn", False),       # Включить бота
        bot_depth=settings.get("bot_depth", 3),      # Глубина поиска бота

        # Отображение названия позиции
        chess_db=chess_db,                           # Подключение к базе данных
        language=settings.get("language", 'EN')     # Язык интерфейса
    )
    game.run()
    
    # Закрытие базы данных
    chess_db.close()
    pygame.quit()

if __name__ == '__main__':
    main()
