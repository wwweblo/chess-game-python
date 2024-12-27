import pygame
import chess

def open(screen, font_family, language):
    # Тексты для кнопок в зависимости от языка
    texts = {
        "EN": ["Queen", "Rook", "Bishop", "Knight"],
        "RU": ["Ферзь", "Ладья", "Слон", "Конь"]
    }

    # Получаем текстовые метки для текущего языка
    labels = texts.get(language, texts["EN"])
    options = [(labels[0], chess.QUEEN), (labels[1], chess.ROOK), (labels[2], chess.BISHOP), (labels[3], chess.KNIGHT)]

    # Получаем размер экрана
    screen_width, screen_height = screen.get_size()

    # Окно для выбора фигуры для превращения пешки
    font = pygame.font.Font(font_family, 50)
    option_rects = []

    # Вычисляем положение кнопок
    button_width = 200
    button_height = 80
    total_height = len(options) * (button_height + 20) - 20  # Общее пространство, занимаемое кнопками
    start_y = (screen_height - total_height) // 2  # Начальная позиция по вертикали

    for i, (text, _) in enumerate(options):
        x = (screen_width - button_width) // 2  # Центрируем по горизонтали
        y = start_y + i * (button_height + 20)
        option_rects.append(pygame.Rect(x, y, button_width, button_height))

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
