import pygame
import time
import chess
from board import draw_board
from bot import ChessBotWrapper
from windows import promotion_window as choose_promotion, color_window as choose_color


class Game:
    def __init__(self, name, window_width, window_height, bot_depth):

        # Инициализация основных параметров
        self.width, self.height = window_width, window_height
        self.square_size = self.width // 8
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(name)

        # Инициализация бота
        self.board = chess.Board()
        self.chess_bot = ChessBotWrapper(depth=bot_depth)

        self.dragging_piece = None
        self.player_color = None    # Цвет игрока
        self.flip_board = False     # Нужно ли переворачивать доску для черных
        self.last_move = None       # Последний ход для подсветки

    def choose_promotion(self):
        return choose_promotion.choose_promotion(self.screen)
    

    def choose_color(self):
        self.player_color = choose_color.choose_color(self.screen)
        if self.player_color == chess.BLACK:
            self.flip_board = True  # Переворачиваем доску для черных
            
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

            # Проверка, является ли ход возможным без продвижения
            if move in self.board.legal_moves:
                self.board.push(move)  # Игрок делает ход
                self.last_move = move  # Сохраняем последний ход игрока
                print(f"User  move: {move}")  # Печать хода игрока
            else:
                # Проверка на возможное продвижение пешки
                piece = self.board.piece_at(self.dragging_piece[0])
                if piece and piece.piece_type == chess.PAWN and chess.square_rank(target_square) in [0, 7]:
                    # Проверка, легален ли ход, если добавить превращение в ферзя
                    promotion_move = chess.Move(self.dragging_piece[0], target_square, promotion=chess.QUEEN)
                    if promotion_move in self.board.legal_moves:
                        # Ход с превращением в ферзя возможен, вызываем выбор фигуры
                        promotion_piece = self.choose_promotion()
                        if promotion_piece:
                            # Создаем ход с выбранной фигурой
                            move = chess.Move(self.dragging_piece[0], target_square, promotion=promotion_piece)
                            self.board.push(move)  # Игрок делает ход
                            self.last_move = move  # Сохраняем последний ход игрока
                            print(f"User  move (promotion): {move}")  # Печать хода с превращением
                        else:
                            print("No promotion piece selected.")  # Если не выбрано
                    else:
                        print(f"Illegal move attempted: {move}")  # Выводим сообщение о недопустимом ходе
                else:
                    print(f"Illegal move attempted: {move}")  # Выводим сообщение о недопустимом ходе

            self.dragging_piece = None