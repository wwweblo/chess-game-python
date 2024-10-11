import pygame
import chess

# Настройки окна
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Загрузка изображений фигур
def load_images():
    piece_types = ['P', 'R', 'N', 'B', 'Q', 'K']
    colors = ['w', 'b']
    images = {}
    for color in colors:
        for piece in piece_types:
            piece_name = color + piece
            images[piece_name] = pygame.transform.scale(
                pygame.image.load(f"images/{piece_name}.png"), (SQUARE_SIZE, SQUARE_SIZE)
            )
    return images

# Рисование доски
def draw_board(screen, is_flipped):
    colors = [WHITE, BLACK]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = colors[(row + col) % 2]
            if is_flipped:
                # Переворачиваем координаты для черных
                col_flipped = BOARD_SIZE - 1 - col
                row_flipped = BOARD_SIZE - 1 - row
                pygame.draw.rect(screen, color, pygame.Rect(col_flipped * SQUARE_SIZE, row_flipped * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Рисование фигур на доске
def draw_pieces(screen, board, images, dragged_piece=None, dragged_pos=None, dragged_square=None, is_flipped=False):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square = row * BOARD_SIZE + col
            piece = board.piece_at(square)
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().upper()
                piece_image = images[piece_color + piece_type]

                if is_flipped:
                    col = BOARD_SIZE - 1 - col
                    row = BOARD_SIZE - 1 - row
                
                # Если перетаскивается эта конкретная фигура, пропускаем её отрисовку на доске
                if dragged_piece and dragged_square == square:
                    continue
                screen.blit(piece_image, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Отрисовка перетаскиваемой фигуры поверх остальных
    if dragged_piece and dragged_pos:
        piece_color = 'w' if dragged_piece.color == chess.WHITE else 'b'
        piece_type = dragged_piece.symbol().upper()
        piece_image = images[piece_color + piece_type]
        screen.blit(piece_image, pygame.Rect(dragged_pos[0] - SQUARE_SIZE // 2, dragged_pos[1] - SQUARE_SIZE // 2, SQUARE_SIZE, SQUARE_SIZE))

# Основная функция игры
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess Game')

    images = load_images()
    board = chess.Board()

    # Выбор цвета
    player_color = choose_color(screen)
    is_flipped = player_color == chess.BLACK
    
    selected_square = None
    dragged_piece = None
    dragged_pos = None
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка клика для выбора фигуры
            if event.type == pygame.MOUSEBUTTONDOWN:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if is_flipped:
                    col = BOARD_SIZE - 1 - col
                    row = BOARD_SIZE - 1 - row
                square = row * BOARD_SIZE + col
                piece = board.piece_at(square)
                if piece and ((piece.color == chess.WHITE and board.turn) or (piece.color == chess.BLACK and not board.turn)):
                    selected_square = square
                    dragged_piece = piece
                    dragged_pos = event.pos  # Начало перетаскивания

            # Обработка перемещения мыши
            if event.type == pygame.MOUSEMOTION and dragged_piece:
                dragged_pos = event.pos  # Обновление позиции перетаскиваемой фигуры

            # Обработка отпускания фигуры
            if event.type == pygame.MOUSEBUTTONUP and dragged_piece:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if is_flipped:
                    col = BOARD_SIZE - 1 - col
                    row = BOARD_SIZE - 1 - row
                target_square = row * BOARD_SIZE + col
                move = chess.Move(selected_square, target_square)
                
                # Проверка, легален ли ход
                if move in board.legal_moves:
                    board.push(move)

                # Сброс перетаскивания
                selected_square = None
                dragged_piece = None
                dragged_pos = None

        draw_board(screen, is_flipped)
        # Передаем координаты и фигуру для корректной отрисовки перетаскивания
        draw_pieces(screen, board, images, dragged_piece, dragged_pos, selected_square, is_flipped)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def choose_color(screen):
    font = pygame.font.Font(None, 48)  # Уменьшение размера шрифта
    text = font.render('Choose Color: White (W) / Black (B)', True, (0, 0, 0))
    
    screen.fill(WHITE)
    
    # Вычисление позиции для центрирования текста по горизонтали
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    screen.blit(text, text_rect)
    pygame.display.flip()
    
    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    return chess.WHITE
                elif event.key == pygame.K_b:
                    return chess.BLACK


if __name__ == "__main__":
    main()
