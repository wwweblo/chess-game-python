import pygame
import chess

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
PIECES = ['P', 'N', 'B', 'R', 'Q', 'K']
COLORS = ['w', 'b']

# Загрузка изображений
def load_images():
    images = {}
    for color in COLORS:
        for piece in PIECES:
            images[color + piece] = pygame.image.load(f'images/{color}{piece}.png')
    return images

# Отрисовка доски
def draw_board(screen, board, images, dragging_piece, mouse_pos):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board.piece_at(chess.square(col, 7-row))
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().upper()
                if dragging_piece and dragging_piece[0] == chess.square(col, 7-row):
                    continue  # Не рисуем фигуру на старой позиции, если она перетаскивается
                # Центрируем фигуру в клетке
                piece_image = images[piece_color + piece_type]
                piece_rect = piece_image.get_rect(center=(col*SQUARE_SIZE + SQUARE_SIZE//2, row*SQUARE_SIZE + SQUARE_SIZE//2))
                screen.blit(piece_image, piece_rect)

    # Рисуем перетаскиваемую фигуру
    if dragging_piece:
        piece_color, piece_type = dragging_piece[1]
        piece_image = images[piece_color + piece_type]
        piece_rect = piece_image.get_rect(center=(mouse_pos[0], mouse_pos[1]))
        screen.blit(piece_image, piece_rect)


# Основная функция игры
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Шахматы')
    images = load_images()
    
    board = chess.Board()
    
    running = True
    dragging_piece = None
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = x // SQUARE_SIZE
                row = 7 - (y // SQUARE_SIZE)
                square = chess.square(col, row)
                piece = board.piece_at(square)
                if piece:
                    piece_color = 'w' if piece.color == chess.WHITE else 'b'
                    piece_type = piece.symbol().upper()
                    dragging_piece = (square, (piece_color, piece_type))
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_piece:
                    x, y = event.pos
                    col = x // SQUARE_SIZE
                    row = 7 - (y // SQUARE_SIZE)
                    target_square = chess.square(col, row)
                    move = chess.Move(dragging_piece[0], target_square)
                    if move in board.legal_moves:
                        board.push(move)
                        print(move)  # Print the move to the console
                    dragging_piece = None
        
        draw_board(screen, board, images, dragging_piece, mouse_pos)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()