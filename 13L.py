import tkinter as tk
import random

CELL = 20
W, H = 25, 20
WALL, EMPTY = 1, 0
grid = []
start = (1, 1)
end = (H - 2, W - 2)
active_paths = []  
visited = set()   
anim_id = None
is_searching = False
final_path = []
path_idx = 0
def generate_maze():
    global grid, end
    grid = [[WALL] * W for _ in range(H)]
    walls = []
    sx, sy = random.randrange(1, H - 1, 2), random.randrange(1, W - 1, 2)
    grid[sx][sy] = EMPTY
    def add_walls(x, y):
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = x + dx, y + dy
            wx, wy = x + dx // 2, y + dy // 2
            if 1 <= nx < H - 1 and 1 <= ny < W - 1 and grid[nx][ny] == WALL:
                walls.append((wx, wy, nx, ny))
    add_walls(sx, sy)
    while walls:
        i = random.randint(0, len(walls) - 1)
        wx, wy, nx, ny = walls.pop(i)
        if grid[nx][ny] == WALL:
            grid[wx][wy] = grid[nx][ny] = EMPTY
            add_walls(nx, ny)
    start_candidates = [(i, j) for i in range(1, H - 1) for j in range(1, W - 1) if grid[i][j] == EMPTY]
    if len(start_candidates) < 2:
        generate_maze()
        return
    s = random.choice(start_candidates)
    start_candidates.remove(s)
    e = random.choice(start_candidates)
    global start, end
    start, end = s, e
def start_dfs_animation():
    global active_paths, visited, is_searching, anim_id, final_path
    if anim_id:
        root.after_cancel(anim_id)
    final_path = []
    active_paths = [[start]]
    visited = {start}
    is_searching = True
    draw()
    root.after(80, step_tree_search)
def step_tree_search():
    global active_paths, visited, anim_id, final_path, is_searching
    if not active_paths or not is_searching:
        return
    new_paths = []
    for path in active_paths:
        x, y = path[-1]  
        if (x, y) == end:
            is_searching = False
            final_path = path
            draw_final_path()
            return   
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < H and 0 <= ny < W and grid[nx][ny] == EMPTY and (nx, ny) not in visited:
                neighbors.append((nx, ny))
                visited.add((nx, ny))
        for nx, ny in neighbors:
            new_paths.append(path + [(nx, ny)])
    active_paths = new_paths
    if active_paths and is_searching:
        anim_id = root.after(80, step_tree_search)
    else:
        is_searching = False
def draw():
    canvas.delete("all")
    for i in range(H):
        for j in range(W):
            fill = "black" if grid[i][j] == WALL else "white"
            x1, y1 = j * CELL, i * CELL
            canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL, fill=fill, outline="gray")
    sx, sy = start
    ex, ey = end
    canvas.create_rectangle(sy * CELL, sx * CELL, sy * CELL + CELL, sx * CELL + CELL, fill="red", stipple="gray50")
    canvas.create_rectangle(ey * CELL, ex * CELL, ey * CELL + CELL, ex * CELL + CELL, fill="green", stipple="gray50")
    if is_searching:
        for x, y in visited:
            if (x, y) != start and (x, y) != end:
                x1, y1 = y * CELL, x * CELL
                canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL, fill="lightblue", outline="gray")
        
        for path in active_paths:
            if path:
                x, y = path[-1]
                if (x, y) != start and (x, y) != end:
                    x1, y1 = y * CELL, x * CELL
                    canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL, fill="orange", outline="darkorange")
def draw_final_path():
    global anim_id
    if anim_id:
        root.after_cancel(anim_id)
    for x, y in visited:
        if (x, y) != start and (x, y) != end:
            x1, y1 = y * CELL, x * CELL
            canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL, fill="lightblue", outline="gray")
    for x, y in final_path:
        if (x, y) != start and (x, y) != end:
            x1, y1 = y * CELL, x * CELL
            canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL, fill="lightgreen", outline="darkgreen")
    root.after(150, animate_bot)
def animate_bot():
    global path_idx, anim_id
    path_idx = 0
    canvas.delete("bot")
    def step():
        global path_idx, anim_id
        if path_idx < len(final_path):
            x, y = final_path[path_idx]
            cx, cy = y * CELL + CELL // 2, x * CELL + CELL // 2
            canvas.delete("bot")
            canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="red", outline="darkred", width=2, tags="bot")
            path_idx += 1
            anim_id = root.after(100, step)
    step()
def click(event):
    global start, end
    x, y = event.y // CELL, event.x // CELL
    if not (0 <= x < H and 0 <= y < W):
        return
    if event.num == 1:
        grid[x][y] = WALL if grid[x][y] != WALL else EMPTY
        draw()
    elif event.num == 3:
        if start == (x, y):
            end = (x, y)
        else:
            start = (x, y)
        draw()
def new_maze():
    global anim_id, is_searching, final_path
    if anim_id:
        root.after_cancel(anim_id)
    is_searching = False
    final_path = []
    generate_maze()
    draw()
def start_search():
    start_dfs_animation()
root = tk.Tk()
root.title("Поиск пути: одновременное расширение всех путей")
canvas = tk.Canvas(root, width=W * CELL, height=H * CELL, bg="gray")
canvas.pack()
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="Новый лабиринт", command=new_maze, width=15).pack(side="left", padx=5)
tk.Button(btn_frame, text="Найти путь", command=start_search, width=15).pack(side="left", padx=5)
canvas.bind("<Button-1>", click)
canvas.bind("<Button-3>", click)
generate_maze()
draw()
root.mainloop()
