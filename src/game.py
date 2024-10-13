import pygame
import time
import chess
from board import draw_board
from bot import ChessBotWrapper

class Game:
    def __init__(self):
        self.width, self.height = 800, 800
        self.square_size = self.width // 8
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Шахматы')
        self.board = chess.Board()
        self.chess_bot = ChessBotWrapper(depth=3)  # Используем ChessBotWrapper
        self.dragging_piece = None
        self.player_color = None  # Цвет игрока
        self.flip_board = False   # Нужно ли переворачивать доску для черных
        self.last_move = None  # Последний ход для подсветки

    def choose_color(self):
        # Создание окна для выбора цвета
        font = pygame.font.SysFont(None, 50)
        white_button = pygame.Rect(150, 300, 200, 100)
        black_button = pygame.Rect(450, 300, 200, 100)

        choosing = True
        while choosing:
            self.screen.fill((255, 255, 255))  # Белый фон
            pygame.draw.rect(self.screen, (200, 200, 200), white_button)
            pygame.draw.rect(self.screen, (100, 100, 100), black_button)

            # Текст на кнопках
            white_text = font.render("Белые", True, (0, 0, 0))
            black_text = font.render("Черные", True, (255, 255, 255))

            # Получаем прямоугольники текста и центрируем их в пределах кнопок
            white_text_rect = white_text.get_rect(center=white_button.center)
            black_text_rect = black_text.get_rect(center=black_button.center)

            # Отрисовываем текст
            self.screen.blit(white_text, white_text_rect)
            self.screen.blit(black_text, black_text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if white_button.collidepoint(event.pos):
                        self.player_color = chess.WHITE
                        choosing = False
                    elif black_button.collidepoint(event.pos):
                        self.player_color = chess.BLACK
                        self.flip_board = True  # Переворачиваем доску для черных
                        choosing = False

    def run(self):
        # Вызов выбора цвета перед началом игры
        self.choose_color()

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_button_up(event)

            # Отрисовка доски с подсветкой последнего хода
            draw_board(self.screen, self.board, self.dragging_piece, mouse_pos, self.flip_board, self.last_move)
            pygame.display.flip()

            # Если очередь бота и цвет бота совпадает с текущим ходом
            if self.board.turn != self.player_color:
                time.sleep(1)
                best_move = self.chess_bot.find_best_move(self.board)
                if best_move:
                    self.board.push(best_move)
                    self.last_move = best_move  # Сохраняем последний ход бота
                    print(f"Bot move: {best_move}")  # Печать хода бота

    def handle_mouse_button_down(self, event):
        x, y = event.pos
        if self.flip_board:
            col = 7 - (x // self.square_size)
            row = y // self.square_size
        else:
            col = x // self.square_size
            row = 7 - (y // self.square_size)

        square = chess.square(col, row)
        piece = self.board.piece_at(square)
        if piece and piece.color == self.player_color:  # Только фигуры игрока можно двигать
            piece_color = 'w' if piece.color == chess.WHITE else 'b'
            piece_type = piece.symbol().upper()
            self.dragging_piece = (square, (piece_color, piece_type))

    def handle_mouse_button_up(self, event):
        if self.dragging_piece:
            x, y = event.pos
            if self.flip_board:
                col = 7 - (x // self.square_size)
                row = y // self.square_size
            else:
                col = x // self.square_size
                row = 7 - (y // self.square_size)

            target_square = chess.square(col, row)
            move = chess.Move(self.dragging_piece[0], target_square)
            if move in self.board.legal_moves:
                self.board.push(move)  # Игрок делает ход
                self.last_move = move  # Сохраняем последний ход игрока
                print(f"User move: {move}")  # Печать хода игрока
            self.dragging_piece = None
