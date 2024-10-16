import pygame
import chess

def choose_color(screen):
    # Создание окна для выбора цвета
    font = pygame.font.SysFont(None, 50)
    white_button = pygame.Rect(150, 300, 200, 100)
    black_button = pygame.Rect(450, 300, 200, 100)

    choosing = True
    while choosing:
        screen.fill((255, 255, 255))  # Белый фон
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