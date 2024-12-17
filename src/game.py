import pygame
import time
import chess
from src.bot import ChessBotWrapper
from src.windows.board import draw_board
from src.windows import (promotion_window,
                         color_window,
                         result_window)


class Game:
    def __init__(self, window_width, window_height, isBotOn=True, bot_depth=3, name='Chess', icon_path='assets/images/icons/icon.png'):

        # Инициализация основных параметров
        self.width, self.height = window_width, window_height
        self.square_size = self.width // 8
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(name)

        # Загрузка иконки
        self.icon_path = icon_path
        try:
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except FileNotFoundError:
            print(f"Icon file not found: {icon_path}")

        # Загрузка звуков
        if not pygame.mixer.get_init():
            pygame.mixer.init()  # Инициализируем pygame.mixer только один раз
        self.move_sound = pygame.mixer.Sound('assets/sounds/move-self.mp3')  # Загрузка звука
        self.capture_sound = pygame.mixer.Sound('assets/sounds/capture.mp3')  # Загрузка звука захвата

        # Инициализация бота
        self.board = chess.Board()
        self.isBotOn = isBotOn
        if self.isBotOn:
            self.chess_bot = ChessBotWrapper(depth=bot_depth)

        self.dragging_piece = None
        self.player_color = None  # Цвет игрока
        self.flip_board = False  # Нужно ли переворачивать доску для черных
        self.last_move = None  # Последний ход для подсветки

        # История ходов
        self.move_history = []
        self.current_move_index = -1

    def choose_promotion(self):
        return promotion_window.open(self.screen)

    def choose_color(self):
        self.player_color = color_window.open(self.screen)
        if self.player_color == chess.BLACK:
            self.flip_board = True  # Переворачиваем доску для черных'

    def run(self):
        """Запуск игры."""
        self.choose_color()

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_button_up(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.undo_move()
                    elif event.key == pygame.K_RIGHT:
                        self.redo_move()

            # Проверяем окончание партии
            if self.board.is_game_over():
                result = self.board.result()
                action = result_window.open(self.screen, result)
                if action == "replay":
                    self.restart_game()
                    return
                elif action == "close":
                    continue  # Закрываем окно результатов, продолжаем просмотр текущей партии

            # Отрисовка доски с подсветкой последнего хода
            draw_board(self.screen, self.board, self.dragging_piece, mouse_pos, self.flip_board, self.last_move)
            pygame.display.flip()

            # Если бот включен и очередь бота
            if self.isBotOn and self.board.turn != self.player_color and self.current_move_index == len(self.move_history) - 1:
                time.sleep(1)
                best_move = self.chess_bot.find_best_move(self.board)
                if best_move is not None:
                    self.execute_move(best_move, is_player=False)

    def restart_game(self):
        """Перезапуск игры."""
        self.board = chess.Board()
        self.move_history = []
        self.current_move_index = -1
        self.dragging_piece = None
        self.last_move = None
        self.flip_board = False
        self.choose_color()

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
        if piece and piece.color == self.board.turn:  # Только фигуры текущего игрока можно двигать
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
                self.execute_move(move, is_player=True)
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
                            self.execute_move(move, is_player=True)
                        else:
                            print('No promotion piece selected.')  # Если не выбрано
                    else:
                        print(f'Illegal move attempted: {move}')  # Выводим сообщение о недопустимом ходе
                else:
                    print(f'Illegal move attempted: {move}')  # Выводим сообщение о недопустимом ходе

            self.dragging_piece = None

    def execute_move(self, move, is_player):
        """Выполняет ход"""
        if self.board.is_capture(move):
            self.capture_sound.play()  # Воспроизведение звука захвата
        else:
            self.move_sound.play()  # Воспроизведение звука обычного хода

        self.board.push(move)
        self.last_move = move  # Сохраняем последний ход

        # Если текущий индекс не указывает на конец истории, обрезаем историю
        if self.current_move_index < len(self.move_history) - 1:
            self.move_history = self.move_history[:self.current_move_index + 1]

        # Добавляем новый ход в историю и обновляем индекс
        self.move_history.append(move)
        self.current_move_index += 1

        if is_player:
            print('-' * 30)
            print(f'User move: {move}')
        else:
            print(f'Bot move: {move}')

    def undo_move(self):
        """Отменяет последний ход, если возможно."""
        if self.current_move_index >= 0:
            self.board.pop()
            self.current_move_index -= 1
            self.last_move = self.move_history[self.current_move_index] if self.current_move_index >= 0 else None
            print("Move undone.")

    def redo_move(self):
        """Повторяет следующий ход из истории, если возможно."""
        if self.current_move_index < len(self.move_history) - 1:
            self.current_move_index += 1
            move = self.move_history[self.current_move_index]
            self.board.push(move)
            self.last_move = move
            print("Move redone.")
