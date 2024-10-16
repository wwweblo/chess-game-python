import pygame
import chess

def choose_promotion(screen):
    # Окно для выбора фигуры для превращения пешки
    font = pygame.font.SysFont(None, 50)
    options = [("Ферзь", chess.QUEEN), ("Ладья", chess.ROOK), ("Слон", chess.BISHOP), ("Конь", chess.KNIGHT)]
    option_rects = []

    # Создаем прямоугольники для каждой кнопки
    for i, (text, _) in enumerate(options):
        option_rects.append(pygame.Rect(200, 100 + i * 100, 200, 80))

    choosing = True
    while choosing:
        screen.fill((255, 255, 255))  # Белый фон

        for i, (text, _) in enumerate(options):
            pygame.draw.rect(screen, (200, 200, 200), option_rects[i])
            option_text = font.render(text, True, (0, 0, 0))
            option_text_rect = option_text.get_rect(center=option_rects[i].center)
            screen.blit(option_text, option_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        return options[i][1]  # Возвращаем выбранную фигуру для превращения
    return None