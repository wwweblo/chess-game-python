import pygame
import chess

def open(screen):
    # Получаем размеры экрана
    screen_width, screen_height = screen.get_size()

    # Адаптивные размеры кнопок
    button_width = screen_width // 4
    button_height = screen_height // 6
    button_gap = screen_width // 8

    # Координаты кнопок
    white_button = pygame.Rect(
        button_gap, screen_height // 2 - button_height // 2, button_width, button_height
    )
    black_button = pygame.Rect(
        screen_width - button_gap - button_width, screen_height // 2 - button_height // 2, button_width, button_height
    )

    # Инициализация шрифта
    font = pygame.font.SysFont(None, screen_width // 15)
    hint_font = pygame.font.SysFont(None, screen_width // 20)

    choosing = True
    while choosing:
        screen.fill((255, 255, 255))  # Белый фон

        # Подсказка пользователю
        hint_text = hint_font.render("Выберите цвет фигур", True, (0, 0, 0))
        hint_text_rect = hint_text.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(hint_text, hint_text_rect)

        # Рисуем кнопки
        pygame.draw.rect(screen, (200, 200, 200), white_button)
        pygame.draw.rect(screen, (100, 100, 100), black_button)

        # Текст на кнопках
        white_text = font.render("Белые", True, (0, 0, 0))
        black_text = font.render("Черные", True, (255, 255, 255))

        # Получаем прямоугольники текста и центрируем их в пределах кнопок
        white_text_rect = white_text.get_rect(center=white_button.center)
        black_text_rect = black_text.get_rect(center=black_button.center)

        # Отрисовываем текст
        screen.blit(white_text, white_text_rect)
        screen.blit(black_text, black_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if white_button.collidepoint(event.pos):
                    return chess.WHITE
                elif black_button.collidepoint(event.pos):
                    return chess.BLACK
    return None
