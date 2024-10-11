import pygame
import chess

# Настройки окна
WIDTH, HEIGHT = 800, 800
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
WHITE = (203, 230, 245)
BLACK = (124, 206, 252)

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
def draw_board(screen):
    colors = [WHITE, BLACK]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Рисование фигур на доске
def draw_pieces(screen, board, images, dragged_piece=None, dragged_pos=None, dragged_square=None):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square = row * BOARD_SIZE + col
            piece = board.piece_at(square)
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().upper()
                piece_image = images[piece_color + piece_type]
                
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
                target_square = row * BOARD_SIZE + col
                move = chess.Move(selected_square, target_square)
                
                # Проверка, легален ли ход
                if move in board.legal_moves:
                    board.push(move)

                # Сброс перетаскивания
                selected_square = None
                dragged_piece = None
                dragged_pos = None

        draw_board(screen)
        # Передаем координаты и фигуру для корректной отрисовки перетаскивания
        draw_pieces(screen, board, images, dragged_piece, dragged_pos, selected_square)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
