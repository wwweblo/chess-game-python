import pygame

def open(screen, result):
    """Отображает результат игры на весь экран с кнопками действий."""
    # Получаем размеры основного окна
    screen_width, screen_height = screen.get_size()

    # Инициализация шрифтов
    font = pygame.font.SysFont(None, screen_width // 15)
    button_font = pygame.font.SysFont(None, screen_width // 20)

    # Определяем текст результата
    if result == '1-0':
        result_text = "Победа белых!"
    elif result == '0-1':
        result_text = "Победа черных!"
    else:
        result_text = "Ничья!"

    # Цвета
    bg_color = (240, 240, 240)
    button_color = (200, 200, 200)
    button_hover_color = (170, 170, 170)
    text_color = (0, 0, 0)

    # Определяем кнопки
    button_width = screen_width // 3
    button_height = screen_height // 10

    close_button = pygame.Rect(
        screen_width // 2 - button_width - 20,  # Смещаем влево от центра
        screen_height // 2 + button_height,    # Располагаем внизу
        button_width,
        button_height
    )

    replay_button = pygame.Rect(
        screen_width // 2 + 20,                # Смещаем вправо от центра
        screen_height // 2 + button_height,   # Располагаем внизу
        button_width,
        button_height
    )

    running = True
    while running:
        screen.fill(bg_color)

        # Текст результата
        result_label = font.render(result_text, True, text_color)
        result_rect = result_label.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(result_label, result_rect)

        # Рисуем кнопки
        mouse_pos = pygame.mouse.get_pos()

        # Кнопка "Закрыть результаты и просмотреть партию"
        if close_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, button_hover_color, close_button)
        else:
            pygame.draw.rect(screen, button_color, close_button)

        close_text = button_font.render("Просмотреть партию", True, text_color)
        close_text_rect = close_text.get_rect(center=close_button.center)
        screen.blit(close_text, close_text_rect)

        # Кнопка "Сыграть снова"
        if replay_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, button_hover_color, replay_button)
        else:
            pygame.draw.rect(screen, button_color, replay_button)

        replay_text = button_font.render("Сыграть снова", True, text_color)
        replay_text_rect = replay_text.get_rect(center=replay_button.center)
        screen.blit(replay_text, replay_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.collidepoint(event.pos):
                    return "close"
                elif replay_button.collidepoint(event.pos):
                    return "replay"
