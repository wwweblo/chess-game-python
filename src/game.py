import pygame
import time
import chess
from src.bot import ChessBotWrapper
from src.windows.board import draw_board
from src.windows import promotion_window, color_window, result_window

class Game:
    def __init__(self, window_width, window_height, isBotOn=True, bot_depth=3, name='Chess', icon_path='assets/images/icons/icon.png', chess_db=None, language='EN'):
        # Инициализация основных параметров
        self.extra_space = 50  # Дополнительное пространство под название позиции
        self.window_width = window_width
        self.window_height = window_height + self.extra_space
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

        self.square_size = self.window_width // 8
        self.current_opening_name = None  # Название текущего дебюта
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(name)
        
        # Подключение к базе данных дебютов
        self.chess_db = chess_db
        self.language = language  # Язык отображения названия дебюта ("EN" или "RU")
        
        self.font = pygame.font.Font('./assets/fonts/graphik_LCG/GraphikLCG-Medium.ttf', 32)

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

        # Название текущего дебюта
        self.current_opening = None

    def choose_promotion(self):
        return promotion_window.open(self.screen)

    def choose_color(self):
        self.player_color = color_window.open(self.screen)
        if self.player_color == chess.BLACK:
            self.flip_board = True  # Переворачиваем доску для черных

    def run(self):
        """Запуск игры."""
        self.choose_color()
        font = pygame.font.Font(None, 36)  # Шрифт для текста

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.isBotOn or self.board.turn == self.player_color:
                        self.handle_mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if not self.isBotOn or self.board.turn == self.player_color:
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
                    continue

            # Отрисовка доски с подсветкой последнего хода
            draw_board(self.screen, self.board, self.dragging_piece, mouse_pos, self.flip_board, self.last_move)

            # Отображение названия дебюта в верхней части
            if self.current_opening_name:
                pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.window_height, self.extra_space))  # Белый фон сверху
                text_surface = self.font.render(f"Opening: {self.current_opening_name}", True, (0, 0, 0))
                self.screen.blit(text_surface, (10, 10))  # Положение текста

            pygame.display.flip()

            # Если бот включен и его очередь
            if self.isBotOn and self.board.turn != self.player_color:
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
        self.current_opening = None
        self.choose_color()

    def handle_mouse_button_down(self, event):
        """Обрабатывает нажатие кнопки мыши и захват фигуры."""
        x, y = event.pos
        # Учитываем дополнительное пространство сверху
        adjusted_y = y - self.extra_space

        if adjusted_y < 0:  # Нажатие выше доски
            return

        if self.flip_board:
            col = 7 - (x // self.square_size)
            row = adjusted_y // self.square_size
        else:
            col = x // self.square_size
            row = 7 - (adjusted_y // self.square_size)

        square = chess.square(col, row)
        piece = self.board.piece_at(square)

        # Разрешаем перетаскивание фигур любого цвета, если бот выключен
        if piece and (not self.isBotOn or piece.color in [chess.WHITE, chess.BLACK]):
            piece_color = 'w' if piece.color == chess.WHITE else 'b'
            piece_type = piece.symbol().upper()
            self.dragging_piece = (square, (piece_color, piece_type))

    def handle_mouse_button_up(self, event):
        """Обрабатывает отпускание кнопки мыши и перемещение фигуры."""
        if self.dragging_piece:
            x, y = event.pos
            # Учитываем дополнительное пространство сверху
            adjusted_y = y - self.extra_space

            if adjusted_y < 0:  # Отпускание выше доски
                self.dragging_piece = None
                return

            if self.flip_board:
                col = 7 - (x // self.square_size)
                row = adjusted_y // self.square_size
            else:
                col = x // self.square_size
                row = 7 - (adjusted_y // self.square_size)

            target_square = chess.square(col, row)
            move = chess.Move(self.dragging_piece[0], target_square)

            # Проверяем валидность хода, даже если бот выключен
            if move in self.board.legal_moves:
                self.execute_move(move, is_player=True)
            else:
                print(f'Illegal move attempted: {move}')

            self.dragging_piece = None

    def execute_move(self, move, is_player):
        """Выполняет ход и обновляет состояние игры."""
        # Проверяем валидность хода перед выполнением
        if move not in self.board.legal_moves:
            print(f"Invalid move: {move}")
            return

        if self.board.is_capture(move):
            self.capture_sound.play()
        else:
            self.move_sound.play()

        self.board.push(move)

        # Обновление истории ходов
        if self.current_move_index < len(self.move_history) - 1:
            # Если мы делаем новый ход после отмены
            self.move_history = self.move_history[:self.current_move_index + 1]

        self.move_history.append(move)
        self.current_move_index += 1

        self.last_move = move

        # Проверка текущей позиции в базе данных
        fen = self.board.fen()
        self.current_opening_name = None
        if self.chess_db:
            opening = self.chess_db.find_opening_by_fen(fen)
            if opening:
                self.current_opening_name = opening[1] if self.language == 'EN' else opening[2]
            else:
                self.current_opening_name = "Unknown Opening"

        if is_player:
            print(f"User move: {move}")
        else:
            print(f"Bot move: {move}")


    def update_opening(self):
        """Обновляет название текущего дебюта на основе позиции."""
        if self.chess_db:
            fen = self.board.fen()
            opening = self.chess_db.find_opening_by_fen(fen)
            if opening:
                self.current_opening = opening[1] if self.language == 'EN' else opening[2]
            else:
                self.current_opening = "Unknown Opening"

    def display_opening_name(self):
        """Отображает название текущего дебюта на экране."""
        if self.current_opening:
            font = pygame.font.Font(None, 36)
            text = font.render(self.current_opening, True, (0, 0, 0))
            self.screen.blit(text, (10, 10))
    def undo_move(self):
        """Откатывает последний ход и синхронизирует состояние доски."""
        if self.current_move_index >= 0:
            self.current_move_index -= 1

            # Пересоздаём состояние доски из истории
            self.board = chess.Board()
            for move in self.move_history[:self.current_move_index + 1]:
                self.board.push(move)

            self.last_move = self.move_history[self.current_move_index] if self.current_move_index >= 0 else None
            print("Move undone. Current turn:", "White" if self.board.turn == chess.WHITE else "Black")

    def redo_move(self):
        """Выполняет следующий ход из истории и синхронизирует состояние доски."""
        if self.current_move_index < len(self.move_history) - 1:
            # Увеличиваем индекс текущего хода
            self.current_move_index += 1

            # Выполняем ход
            move = self.move_history[self.current_move_index]
            self.board.push(move)

            # Обновляем последний ход
            self.last_move = move

            # Проверка состояния очереди (обновляем очередь)
            print("Move redone. Current turn:", "White" if self.board.turn == chess.WHITE else "Black")