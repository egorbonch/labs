import tkinter as tk
from tkinter import messagebox
import random

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = 0

    def is_sunk(self):
        return self.hits == self.size


class BattleshipGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Морской бой")
        self.root.geometry("800x600")
        self.player_board = [[0]*10 for _ in range(10)]  # 0=пусто, 1=корабль, 2=попадание, 3=промах
        self.bot_board = [[0]*10 for _ in range(10)]     # 0=пусто, 1=корабль, 2=попадание, 3=промах
        self.player_ships = []
        self.bot_ships = []
        self.ship_sizes = [4,3,3,2,2,2,1,1,1,1]
        self.current_ship_size_index = 0
        self.ship_orientation = "horizontal"
        self.player_turn = True
        self.game_started = False
        self.bot_hunt_stack = []
        self.bot_last_hit = None
        self.bot_hunt_direction = None
        self.bot_probability_map = [[0]*10 for _ in range(10)]
        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Добро пожаловать!", font=("Arial",20,"bold"), fg="darkblue").pack(pady=10)
        tk.Label(self.root, text="МОРСКОЙ БОЙ", font=("Arial",24,"bold"), fg="blue").pack(pady=10)
        tk.Button(self.root, text="Начать игру", font=("Arial",14), command=self.start_game,
                  bg="lightgreen", width=20, height=2).pack(pady=10)
        tk.Button(self.root, text="Помощь", font=("Arial",14), command=self.show_help,
                  bg="lightblue", width=20, height=2).pack(pady=10)

    def show_help(self):
        help_text = """Цель: первым потопить все корабли противника.

Корабли: 1×4, 2×3, 3×2, 4×1.
Правила: корабли не касаются друг друга.
Управление: ЛКМ — стрельба/размещение, кнопка — поворот."""
        messagebox.showinfo("Помощь", help_text)

    def start_game(self):
        self.create_ship_placement_window()

    def create_ship_placement_window(self):
        self.clear_window()
        tk.Label(self.root, text="РАССТАНОВКА КОРАБЛЕЙ", font=("Arial",18,"bold")).pack(pady=10)
        info_text = f"Разместите корабль: {self.ship_sizes[self.current_ship_size_index]} клетки"
        self.info_label = tk.Label(self.root, text=info_text, font=("Arial",12))
        self.info_label.pack()
        orient_text = f"Ориентация: {'Горизонтальная' if self.ship_orientation == 'horizontal' else 'Вертикальная'}"
        self.orient_label = tk.Label(self.root, text=orient_text, font=("Arial",10), fg="darkgreen")
        self.orient_label.pack()
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Повернуть", command=self.toggle_orientation).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Авто", command=self.random_placement).pack(side=tk.LEFT, padx=5)
        self.create_board_with_coords()

    def create_board_with_coords(self):
        board_container = tk.Frame(self.root)
        board_container.pack(pady=20)
        letters_frame = tk.Frame(board_container)
        letters_frame.pack()
        tk.Label(letters_frame, width=3).grid(row=0, column=0)
        for j in range(10):
            tk.Label(letters_frame, text=chr(65+j), width=3, font=("Arial",10,"bold")).grid(row=0, column=j+1)
        self.board_frame = tk.Frame(board_container)
        self.board_frame.pack()
        self.buttons = [[None]*10 for _ in range(10)]
        for i in range(10):
            tk.Label(self.board_frame, text=str(i+1), width=3, font=("Arial",10,"bold")).grid(row=i, column=0)
            for j in range(10):
                btn = tk.Button(self.board_frame, width=3, height=1, bg="lightblue",
                               command=lambda x=i, y=j: self.place_ship(x, y))
                btn.grid(row=i, column=j+1, padx=1, pady=1)
                btn.bind("<Enter>", lambda e, x=i, y=j: self.show_preview(x, y))
                btn.bind("<Leave>", lambda e: self.hide_preview())
                self.buttons[i][j] = btn

    def toggle_orientation(self):
        self.ship_orientation = "vertical" if self.ship_orientation == "horizontal" else "horizontal"
        self.orient_label.config(text=f"Ориентация: {'Горизонтальная' if self.ship_orientation == 'horizontal' else 'Вертикальная'}")

    def show_preview(self, x, y):
        size = self.ship_sizes[self.current_ship_size_index]
        positions, valid = [], True
        if self.ship_orientation == "horizontal":
            if y + size > 10 or any(self.player_board[x][y+i] for i in range(size)): valid = False
            else: positions = [(x, y+i) for i in range(size)]
        else:
            if x + size > 10 or any(self.player_board[x+i][y] for i in range(size)): valid = False
            else: positions = [(x+i, y) for i in range(size)]
        if not valid: return
        for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            for px,py in positions:
                nx, ny = px+dx, py+dy
                if 0<=nx<10 and 0<=ny<10 and self.player_board[nx][ny]:
                    valid = False; break
            if not valid: break
        for px,py in positions:
            self.buttons[px][py].config(bg="lightgreen" if valid else "salmon")

    def hide_preview(self):
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].config(bg="gray" if self.player_board[i][j]==1 else "lightblue")

    def place_ship(self, x, y):
        size = self.ship_sizes[self.current_ship_size_index]
        if self.ship_orientation == "horizontal":
            if y + size > 10 or any(self.player_board[x][y+i] for i in range(size)): return
            positions = [(x, y+i) for i in range(size)]
        else:
            if x + size > 10 or any(self.player_board[x+i][y] for i in range(size)): return
            positions = [(x+i, y) for i in range(size)]
        for px,py in positions:
            for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                nx, ny = px+dx, py+dy
                if 0<=nx<10 and 0<=ny<10 and self.player_board[nx][ny] and (nx,ny) not in positions:
                    return
        ship = Ship(size)
        for pos in positions:
            self.player_board[pos[0]][pos[1]] = 1
            self.buttons[pos[0]][pos[1]].config(bg="gray")
            ship.positions.append(pos)
        self.player_ships.append(ship)
        self.current_ship_size_index += 1
        if self.current_ship_size_index >= len(self.ship_sizes):
            self.finish_ship_placement()
        else:
            self.info_label.config(text=f"Разместите корабль: {self.ship_sizes[self.current_ship_size_index]} клетки")

    def random_placement(self):
        self.player_board = [[0]*10 for _ in range(10)]
        self.player_ships = []
        self.current_ship_size_index = 0
        for size in self.ship_sizes:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                orientation = random.choice(["horizontal", "vertical"])
                x = random.randint(0, 9 if orientation=="horizontal" else 10-size)
                y = random.randint(0, 10-size if orientation=="horizontal" else 9)
                positions = [(x + (i if orientation=="vertical" else 0), y + (i if orientation=="horizontal" else 0)) for i in range(size)]
                valid = True
                for px,py in positions:
                    if not (0<=px<10 and 0<=py<10) or self.player_board[px][py]: valid = False; break
                    for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        nx, ny = px+dx, py+dy
                        if 0<=nx<10 and 0<=ny<10 and self.player_board[nx][ny] and (nx,ny) not in positions:
                            valid = False; break
                    if not valid: break
                if valid:
                    ship = Ship(size)
                    for pos in positions:
                        self.player_board[pos[0]][pos[1]] = 1
                        ship.positions.append(pos)
                    self.player_ships.append(ship)
                    placed = True
                attempts += 1
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].config(bg="gray" if self.player_board[i][j]==1 else "lightblue")
        self.finish_ship_placement()

    def finish_ship_placement(self):
        self.setup_bot_ships()
        self.start_battle()

    def setup_bot_ships(self):
        self.bot_board = [[0]*10 for _ in range(10)]
        self.bot_ships = []
        sizes_sorted = sorted(self.ship_sizes, reverse=True)
        for size in sizes_sorted:
            placed = False
            attempts = 0
            while not placed and attempts < 500:
                orientation = random.choice(["horizontal", "vertical"])
                x = random.randint(0, 9 if orientation=="horizontal" else 10-size)
                y = random.randint(0, 10-size if orientation=="horizontal" else 9)
                positions = [(x + (i if orientation=="vertical" else 0), y + (i if orientation=="horizontal" else 0)) for i in range(size)]
                valid = True
                for px,py in positions:
                    if not (0<=px<10 and 0<=py<10) or self.bot_board[px][py]: valid = False; break
                    for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        nx, ny = px+dx, py+dy
                        if 0<=nx<10 and 0<=ny<10 and self.bot_board[nx][ny] and (nx,ny) not in positions:
                            valid = False; break
                    if not valid: break
                if valid:
                    ship = Ship(size)
                    for pos in positions:
                        self.bot_board[pos[0]][pos[1]] = 1
                        ship.positions.append(pos)
                    self.bot_ships.append(ship)
                    placed = True
                attempts += 1

    def start_battle(self):
        self.clear_window()
        self.game_started = True
        tk.Label(self.root, text="БОЙ НАЧАЛСЯ!", font=("Arial",18,"bold")).pack(pady=10)
        boards_frame = tk.Frame(self.root)
        boards_frame.pack(pady=20)
        self.create_battle_board(boards_frame, "Ваше поле", self.player_board, 0, False)
        self.create_battle_board(boards_frame, "Поле бота", self.bot_board, 1, True)
        self.status_label = tk.Label(self.root, text="Ваш ход!", font=("Arial",14), fg="green")
        self.status_label.pack(pady=10)

    def create_battle_board(self, parent, title, board, column, interactive):
        frame = tk.Frame(parent)
        frame.grid(row=0, column=column, padx=20)
        tk.Label(frame, text=title, font=("Arial",12,"bold")).pack()
        coords_frame = tk.Frame(frame)
        coords_frame.pack()
        tk.Label(coords_frame, width=3).grid(row=0, column=0)
        for j in range(10):
            tk.Label(coords_frame, text=chr(65+j), width=3, font=("Arial",10,"bold")).grid(row=0, column=j+1)
        board_frame = tk.Frame(frame)
        board_frame.pack(pady=10)
        buttons = [[None]*10 for _ in range(10)]
        for i in range(10):
            tk.Label(board_frame, text=str(i+1), width=3, font=("Arial",10,"bold")).grid(row=i, column=0)
            for j in range(10):
                if interactive:
                    btn = tk.Button(board_frame, width=3, height=1, bg="lightblue",
                                   command=lambda x=i, y=j: self.player_move(x, y))
                else:
                    color = "gray" if board[i][j]==1 else "lightblue"
                    btn = tk.Button(board_frame, width=3, height=1, bg=color, state=tk.DISABLED)
                btn.grid(row=i, column=j+1, padx=1, pady=1)
                buttons[i][j] = btn
        if interactive:
            self.bot_buttons = buttons
        else:
            self.player_buttons = buttons

    def player_move(self, x, y):
        if not self.player_turn or self.bot_board[x][y] in (2,3): return
        if self.bot_board[x][y] == 1:
            self.bot_board[x][y] = 2
            self.bot_buttons[x][y].config(bg="red", text="X", state=tk.DISABLED)
            for ship in self.bot_ships:
                if (x,y) in ship.positions:
                    ship.hits += 1
                    if ship.is_sunk():
                        self.status_label.config(text="Вы потопили корабль!")
                        for px,py in ship.positions:
                            for dx in (-1,0,1):
                                for dy in (-1,0,1):
                                    nx, ny = px+dx, py+dy
                                    if 0<=nx<10 and 0<=ny<10 and self.bot_board[nx][ny]==0:
                                        self.bot_board[nx][ny] = 3
                                        self.bot_buttons[nx][ny].config(bg="yellow", text="•", state=tk.DISABLED)
                    else:
                        self.status_label.config(text="Попадание! Ходите снова!")
                    break
        else:
            self.bot_board[x][y] = 3
            self.bot_buttons[x][y].config(bg="yellow", text="•", state=tk.DISABLED)
            self.status_label.config(text="Промах! Ход бота.")
            self.player_turn = False
            self.root.after(400, self.bot_move)
        if all(ship.is_sunk() for ship in self.bot_ships):
            self.game_over("Вы победили!")

    def update_probability_map(self):
        self.bot_probability_map = [[0]*10 for _ in range(10)]
        for ship_size in set(self.ship_sizes):
            for i in range(10):
                for j in range(10):
                    # Горизонтально
                    if j <= 10 - ship_size:
                        valid = True
                        for k in range(ship_size):
                            if self.player_board[i][j+k] == 3:
                                valid = False
                                break
                        if valid:
                            for k in range(ship_size):
                                if self.player_board[i][j+k] != 3:
                                    self.bot_probability_map[i][j+k] += 1
                    # Вертикально
                    if i <= 10 - ship_size:
                        valid = True
                        for k in range(ship_size):
                            if self.player_board[i+k][j] == 3:
                                valid = False
                                break
                        if valid:
                            for k in range(ship_size):
                                if self.player_board[i+k][j] != 3:
                                    self.bot_probability_map[i+k][j] += 1

    def bot_move(self):
        # Приоритет: охота
        if self.bot_hunt_stack:
            x, y = self.bot_hunt_stack.pop(0)
            if 0 <= x < 10 and 0 <= y < 10 and self.player_board[x][y] not in (2, 3):
                self.execute_bot_shot(x, y)
                return
        
        # Если есть последнее попадание, но нет стека — генерируем соседей
        if self.bot_last_hit and not self.bot_hunt_stack and self.bot_hunt_direction is None:
            x, y = self.bot_last_hit
            directions = [(0,1), (1,0), (0,-1), (-1,0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] not in (2, 3):
                    self.bot_hunt_stack.append((nx, ny))
            if self.bot_hunt_stack:
                x, y = self.bot_hunt_stack.pop(0)
                self.execute_bot_shot(x, y)
                return

        # Иначе — стрельба по карте вероятностей
        self.update_probability_map()
        max_prob = -1
        best_cells = []
        for i in range(10):
            for j in range(10):
                if self.player_board[i][j] not in (2, 3):
                    prob = self.bot_probability_map[i][j]
                    if (i + j) % 2 == 0:
                        prob += 5
                    center_dist = abs(i - 4.5) + abs(j - 4.5)
                    prob += (9 - center_dist) * 0.3
                    if prob > max_prob:
                        max_prob = prob
                        best_cells = [(i, j)]
                    elif prob == max_prob:
                        best_cells.append((i, j))

        if best_cells:
            x, y = random.choice(best_cells)
            self.execute_bot_shot(x, y)
        else:
            empty_cells = [(i,j) for i in range(10) for j in range(10) if self.player_board[i][j] not in (2, 3)]
            if empty_cells:
                x, y = random.choice(empty_cells)
                self.execute_bot_shot(x, y)
            else:
                self.player_turn = True
                self.status_label.config(text="Ваш ход!")

    def execute_bot_shot(self, x, y):
        if self.player_board[x][y] == 1:
            self.player_board[x][y] = 2
            self.player_buttons[x][y].config(bg="red", text="X")
            
            # Найти корабль
            hit_ship = None
            for ship in self.player_ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    hit_ship = ship
                    break

            self.bot_last_hit = (x, y)
            
            # Если корабль потоплен
            if hit_ship and hit_ship.is_sunk():
                # Отметить зону вокруг
                for px, py in hit_ship.positions:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] == 0:
                                self.player_board[nx][ny] = 3
                                self.player_buttons[nx][ny].config(bg="yellow", text="•")
                # Сброс охоты
                self.bot_hunt_stack = []
                self.bot_last_hit = None
                self.bot_hunt_direction = None
                self.status_label.config(text="Бот потопил ваш корабль!")
                self.root.after(400, self.bot_move)
            else:
                # Корабль ранен — определяем направление после 2+ попаданий
                hits_on_ship = [pos for pos in hit_ship.positions if self.player_board[pos[0]][pos[1]] == 2]
                if len(hits_on_ship) >= 2:
                    hits_on_ship.sort()
                    # Проверка направления
                    if all(p[0] == hits_on_ship[0][0] for p in hits_on_ship):  # горизонталь
                        self.bot_hunt_direction = (0, 1)
                    elif all(p[1] == hits_on_ship[0][1] for p in hits_on_ship):  # вертикаль
                        self.bot_hunt_direction = (1, 0)
                    else:
                        self.bot_hunt_direction = None

                    # Генерация клеток для обстрела: до начала и после конца
                    self.bot_hunt_stack = []
                    start = min(hits_on_ship)
                    end = max(hits_on_ship)
                    
                    if self.bot_hunt_direction == (0, 1):  # горизонталь
                        # Влево
                        ny = start[1] - 1
                        if ny >= 0 and self.player_board[start[0]][ny] not in (2, 3):
                            self.bot_hunt_stack.append((start[0], ny))
                        # Вправо
                        ny = end[1] + 1
                        if ny < 10 and self.player_board[end[0]][ny] not in (2, 3):
                            self.bot_hunt_stack.append((end[0], ny))
                    elif self.bot_hunt_direction == (1, 0):  # вертикаль
                        # Вверх
                        nx = start[0] - 1
                        if nx >= 0 and self.player_board[nx][start[1]] not in (2, 3):
                            self.bot_hunt_stack.append((nx, start[1]))
                        # Вниз
                        nx = end[0] + 1
                        if nx < 10 and self.player_board[nx][end[1]] not in (2, 3):
                            self.bot_hunt_stack.append((nx, end[1]))
                else:
                    # Первое попадание — добавляем соседей (если стек пуст)
                    if not self.bot_hunt_stack and self.bot_hunt_direction is None:
                        directions = [(0,1), (1,0), (0,-1), (-1,0)]
                        for dx, dy in directions:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] not in (2, 3):
                                self.bot_hunt_stack.append((nx, ny))
                
                self.status_label.config(text="Бот попал!")
                self.root.after(400, self.bot_move)
        else:
            self.player_board[x][y] = 3
            self.player_buttons[x][y].config(bg="yellow", text="•")
            self.status_label.config(text="Ваш ход!")
            self.player_turn = True

        if all(ship.is_sunk() for ship in self.player_ships):
            self.game_over("Бот победил!")

    def game_over(self, message):
        self.game_started = False
        messagebox.showinfo("Игра окончена", message)
        tk.Button(self.root, text="Новая игра", command=self.restart_game,
                 font=("Arial",12), bg="lightgreen").pack(pady=10)
        tk.Button(self.root, text="Меню", command=self.create_welcome_screen,
                 font=("Arial",12), bg="lightblue").pack(pady=5)

    def restart_game(self):
        self.__init__()
        self.create_ship_placement_window()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = BattleshipGame()
    game.run()
