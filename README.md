# ♟️Chess Game
![board start position](assets/images/docs-images/board-start-pos.png)

## Run the game
run the game by executing the following command in your terminal:
```bash
python main.py
```

While game is running you can undo and redo moves by pressing `left arrow` and `right arrow` keys.

## ⚙️ Settings
All settings are stored in the `user_setings.txt` file.

- `window_autosize` - True or False, whether the window should autosize to the board size.
- `window_width`, `window_height` - lets user to size the window manually if `window_autosize = False`.
- `isBotOn` - True or False, whether the bot is on or off.
- `bot_depth` - depth of the bot's search tree. Works only when `isBotOn = True`.
- `language` - EN or RU , language of the game.
- `db_path` - path to the database file.

## 💻 Dependencies
Stored in `DEPENDENCIES.txt` file.
- `pygame` - for graphics, sounds and window management
- `chess` - for game logic

To download them, run this in terminal:
```bash
pip install pygame
pip install chess
```

also used in project:
- os
- time
- sqlite3

## 📄 Database
Used in this project to show position name
![db usege](assets\images\docs-images\italian-game-pos.png)
Database is stored in `data/openings/chess_openings` folder.

### Tables
#### Openings
||Name|Type|Not null|
|---|---|---|---|
|Primary key|id|integer|not null|
|Foreign key|opening_id|integer|not null|
|Foreign key|variation_id|integer||
||move|text|not null|
|unique|fen|text|not null|

#### OpeningsMain
||Name|Type|Not null|
|---|---|---|---|
|Primary key|id|integer|not null|
|unique|name_en|text|not null|
|unique|name_ru|text|not null|

#### OpeningsVariations
||Name|Type|Not null|
|---|---|---|---|
|Primary key|id|integer|not null|
|unique|variation_name_en|text|not null|
|unique|variation_name_ru|text|not null|

### To add new openings into the base:
1. run `src\db\old\database.py`

```
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
P P P P P P P P
R N B Q K B N R
Введите ваш ход в формате SAN (например, Nf3) или 'back' для отмены последнего хода, или 'rn' для переименования дебюта:
Ход: e4
EN: King's Pawn Opening
RU: Дебют королевской пешки
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . P . . .
. . . . . . . .
P P P P . P P P
R N B Q K B N R
```
if current position is not into the base you will be asked to name it on english and russian. Separate opening name and variation name with `:`

2. Run `src\db\migration.py` to convert old database to new one.
