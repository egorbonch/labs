import tkinter as tk
from tkinter import Canvas, colorchooser, filedialog, messagebox
import csv
import math
from shapely.geometry import Polygon  # Убедитесь, что установлен: pip install shapely

class SectorApp:
    def __init__(self, master):
        self.master = master
        self.master.configure(background="#A8E4A0")

        self.canvas = Canvas(master, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.current_sector = None  # [x, y, r, start_angle, extent, color]
        self.selected_sector = None
        self.sectors = []  # [(x, y, r, start_angle, extent, color)]
        self.id_map = {}
        self.current_color = "#FF0000"

        self.bind_events()

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def on_left_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_sector = [event.x, event.y, 0, 0, 90, self.current_color]

    def on_drag(self, event):
        if self.current_sector:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            radius = int(math.hypot(dx, dy))
            self.current_sector[2] = radius
            self.redraw_canvas()

    def on_release(self, event):
        if self.current_sector:
            self.sectors.append(tuple(self.current_sector))
            self.current_sector = None
            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.id_map = {}
        for idx, (x, y, r, sa, ea, color) in enumerate(self.sectors):
            coords = self.get_arc_coords(x, y, r, sa, ea)
            poly_id = self.canvas.create_polygon(coords, fill=color, outline="black", width=2)
            self.id_map[poly_id] = idx
        if self.current_sector:
            coords = self.get_arc_coords(*self.current_sector)
            self.canvas.create_polygon(coords, fill=self.current_sector[5], outline="black", width=2)

    def get_arc_coords(self, x, y, r, start_angle, extent):
        """Возвращает список кортежей (x, y), представляющих сектор"""
        points = [(x, y)]  # Центр
        steps = 30
        for i in range(steps + 1):
            angle = math.radians(start_angle + (i * extent / steps))
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))
        return points

    def on_right_click(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in items:
            if self.canvas.type(item) == 'polygon' and item in self.id_map:
                self.selected_sector = self.id_map[item]
                messagebox.showinfo("Выбран сектор", f"Сектор {self.selected_sector}")
                break

    def rotate_sector(self, angle=45):
        if self.selected_sector is None:
            messagebox.showwarning("Ошибка", "Выберите сектор правой кнопкой мыши.")
            return

        x, y, r, sa, ea, color = self.sectors[self.selected_sector]
        sa = (sa + angle) % 360
        self.sectors[self.selected_sector] = (x, y, r, sa, ea, color)
        self.redraw_canvas()

    def choose_color(self):
        _, hex_color = colorchooser.askcolor()
        if hex_color:
            self.current_color = hex_color
            if self.selected_sector is not None:
                x, y, r, sa, ea, _ = self.sectors[self.selected_sector]
                self.sectors[self.selected_sector] = (x, y, r, sa, ea, hex_color)
                self.redraw_canvas()

    def delete_selected(self):
        if self.selected_sector is None:
            messagebox.showwarning("Ошибка", "Выберите сектор правой кнопкой мыши.")
            return
        del self.sectors[self.selected_sector]
        self.selected_sector = None
        self.redraw_canvas()

    def check_intersection(self):
        polygons = []
        for idx, (x, y, r, sa, ea, _) in enumerate(self.sectors):
            coords = self.get_arc_coords(x, y, r, sa, ea)
            polygon = Polygon(coords)
            if polygon.is_valid:
                polygons.append((idx, polygon))

        n = len(polygons)
        message = "Пересечения найдены между следующими секторами:\n"
        intersections_found = False

        for i in range(n):
            for j in range(i + 1, n):
                if polygons[i][1].intersects(polygons[j][1]):
                    intersections_found = True
                    message += f"- Сектор {polygons[i][0]} и {polygons[j][0]}\n"

        if intersections_found:
            messagebox.showinfo("Пересечение", message)
        else:
            messagebox.showinfo("Пересечение", "Нет пересечений.")

    def clear_canvas(self):
        self.sectors = []
        self.selected_sector = None
        self.canvas.delete("all")

    def save_sectors(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "X", "Y", "Radius", "StartAngle", "Extent", "Color"])
                for i, (x, y, r, sa, ea, color) in enumerate(self.sectors):
                    writer.writerow([i, x, y, r, sa, ea, color])
            messagebox.showinfo("Сохранено", "Данные сохранены!")

    def load_sectors(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    self.sectors = []
                    for row in reader:
                        i, x, y, r, sa, ea, color = row
                        self.sectors.append((int(x), int(y), int(r), float(sa), float(ea), color))
                    self.redraw_canvas()
                    messagebox.showinfo("Загружено", "Данные загружены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Файл повреждён или имеет неверный формат.\n{e}")


class Interface(tk.Frame):
    def __init__(self, app):
        super().__init__(app.master)
        self.app = app
        self.initUI()

    def initUI(self):
        self.pack(fill=tk.X)
        self.config(background="#A8E4B9")

        button_frame = tk.Frame(self, bg="#A8E4B9")
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        buttons = [
            ("Загрузить", app.load_sectors),
            ("Цвет", app.choose_color),
            ("Удалить", app.delete_selected),
            ("Повернуть", app.rotate_sector),
            ("Пересечение", app.check_intersection),
            ("Очистить", app.clear_canvas),
            ("Сохранить", app.save_sectors),
        ]

        total_columns = len(buttons)
        for col, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command)
            btn.grid(row=0, column=col, sticky="ew", padx=4, pady=4)

        for col in range(total_columns):
            button_frame.grid_columnconfigure(col, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Лабораторная работа №8 — Сектора круга")
    root.geometry("1200x700")

    app = SectorApp(root)
    interface = Interface(app)

    root.mainloop()
