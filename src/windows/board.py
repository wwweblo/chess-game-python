# board.py
import pygame
import chess

COLORS = ['w', 'b']
PIECES = ['P', 'N', 'B', 'R', 'Q', 'K']

def load_images():
    '''Загрузка изображений фигур на доске'''
    images = {}
    for color in COLORS:
        for piece in PIECES:
            images[color + piece] = pygame.image.load(f'assets/images/pieces/wikipedia/{color}{piece}.png')
    return images

def draw_board(screen, board, dragging_piece, mouse_pos, flip_board=False, last_move=None):
    """Отрисовка доски с подсветкой последнего хода и перетаскиванием фигуры."""
    images = load_images()
    colors = [(235, 235, 208), (119, 148, 85)]  # Белый и серый в RGB
    highlight_color = (255, 255, 0, 160)  # Желтый с альфа-каналом

    square_size = screen.get_width() // 8

    # Создаем временную поверхность для подсветки с поддержкой альфа-канала
    highlight_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)

    for row in range(8):
        for col in range(8):
            # Если доска перевернута, строки и столбцы должны отображаться зеркально
            display_row = 7 - row if flip_board else row
            display_col = 7 - col if flip_board else col

            # Определение цвета клетки
            color = colors[(row + col) % 2]

            pygame.draw.rect(screen, color, pygame.Rect(display_col * square_size, display_row * square_size + 50, square_size, square_size))

            # Подсветка клеток последнего хода
            if last_move:
                if chess.square(col, 7 - row) in (last_move.from_square, last_move.to_square):
                    highlight_surface.fill(highlight_color)
                    screen.blit(highlight_surface, (display_col * square_size, display_row * square_size + 50))

            # Отображение фигуры
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().upper()
                if dragging_piece and dragging_piece[0] == chess.square(col, 7 - row):
                    continue  # Не рисуем фигуру на старой позиции, если она перетаскивается
                piece_image = images[piece_color + piece_type]
                piece_rect = piece_image.get_rect(center=(display_col * square_size + square_size // 2, display_row * square_size + square_size // 2 + 50))
                screen.blit(piece_image, piece_rect)

    # Рисуем перетаскиваемую фигуру
    if dragging_piece:
        piece_color, piece_type = dragging_piece[1]
        piece_image = images[piece_color + piece_type]
        piece_rect = piece_image.get_rect(center=(mouse_pos[0], mouse_pos[1]))
        screen.blit(piece_image, piece_rect)
