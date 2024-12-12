import pygame

def open(screen, result):
    """Отображает результат игры в отдельном оверлейном окне."""
    # Получаем размеры основного окна
    screen_width, screen_height = screen.get_size()

    # Размеры окна результата
    window_width = screen_width // 2
    window_height = screen_height // 3

    # Создаем поверхность для результата
    result_window = pygame.Surface((window_width, window_height))
    result_window.fill((240, 240, 240))

    # Инициализация шрифтов
    font = pygame.font.SysFont(None, screen_width // 15)
    message_font = pygame.font.SysFont(None, screen_width // 25)

    # Определяем текст результата
    if result == '1-0':
        result_text = "Победа белых!"
    elif result == '0-1':
        result_text = "Победа черных!"
    else:
        result_text = "Ничья!"

    # Текст результата
    result_label = font.render(result_text, True, (0, 0, 0))
    result_rect = result_label.get_rect(center=(window_width // 2, window_height // 3))
    result_window.blit(result_label, result_rect)

    # Сообщение пользователю
    message_label = message_font.render("Нажмите любую клавишу, чтобы продолжить", True, (100, 100, 100))
    message_rect = message_label.get_rect(center=(window_width // 2, 2 * window_height // 3))
    result_window.blit(message_label, message_rect)

    running = True
    while running:
        # Рисуем окно результата по центру поверх основного экрана
        screen.blit(result_window, ((screen_width - window_width) // 2, (screen_height - window_height) // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False
