import tkinter as tk
from tkinter import messagebox, ttk
import sys


DISK_COLORS = [
    "#FF6B6B", "#FFA07A", "#FFD93D", "#6BCB77",
    "#4D96FF", "#9B59B6", "#E056A0", "#00CEC9",
]
PEG_COLOR = "#5D4037"
BG_COLOR = "#1a1a2e"
PANEL_COLOR = "#16213e"
BASE_COLOR = "#3E2723"
TEXT_COLOR = "#ECF0F1"
HIGHLIGHT_COLOR = "#F1C40F"
MOVE_TEXT_COLOR = "#3498DB"
WIN_COLOR = "#2ECC71"
SHADOW_COLOR = "#0d1117"


class TowerOfHanoi:
    def __init__(self, root):
        self.root = root
        self.root.title("Ханойская пирамида")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.num_disks = 5
        self.pegs = [[], [], []]
        self.moves = 0
        self.selected_peg = None
        self.animating = False
        self.solution_moves = []
        self.solution_idx = 0
        self.in_solution = False

        self.canvas_width = 900
        self.canvas_height = 420
        self.base_y = 370
        self.peg_x = [150, 450, 750]
        self.disk_height = 30
        self.max_disk_width = 180
        self.min_disk_width = 50

        self._build_ui()
        self._reset_game()

    def _build_ui(self):
        top = tk.Frame(self.root, bg=PANEL_COLOR, pady=8)
        top.pack(fill=tk.X)

        tk.Label(
            top, text="🏗  Ханойская пирамида", font=("Segoe UI", 18, "bold"),
            bg=PANEL_COLOR, fg=TEXT_COLOR,
        ).pack()

        info = tk.Frame(self.root, bg=BG_COLOR)
        info.pack(fill=tk.X, padx=20, pady=(8, 0))

        self.moves_label = tk.Label(
            info, text="Ходы: 0", font=("Segoe UI", 13, "bold"),
            bg=BG_COLOR, fg=MOVE_TEXT_COLOR,
        )
        self.moves_label.pack(side=tk.LEFT)

        self.min_label = tk.Label(
            info, text="", font=("Segoe UI", 11),
            bg=BG_COLOR, fg="#7F8C8D",
        )
        self.min_label.pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(
            info, text="Перенесите все диски на третий стержень",
            font=("Segoe UI", 11), bg=BG_COLOR, fg="#BDC3C7",
        )
        self.status_label.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width, height=self.canvas_height,
            bg=BG_COLOR, highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)

        controls = tk.Frame(self.root, bg=PANEL_COLOR, pady=10)
        controls.pack(fill=tk.X)

        tk.Label(
            controls, text="Диски:", font=("Segoe UI", 11),
            bg=PANEL_COLOR, fg=TEXT_COLOR,
        ).pack(side=tk.LEFT, padx=(20, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TSpinbox",
            fieldbackground="#1a1a2e", background=PANEL_COLOR,
            foreground=TEXT_COLOR, arrowcolor=TEXT_COLOR,
        )

        self.disk_var = tk.IntVar(value=self.num_disks)
        spinbox = ttk.Spinbox(
            controls, from_=3, to=8, width=4,
            textvariable=self.disk_var, font=("Segoe UI", 11),
            command=self._on_disk_change,
        )
        spinbox.pack(side=tk.LEFT, padx=5)

        btn_cfg = dict(
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
            padx=16, pady=4, cursor="hand2", bd=0,
        )

        tk.Button(
            controls, text="🔄 Новая игра", bg="#3498DB", fg="white",
            activebackground="#2980B9", activeforeground="white",
            command=self._reset_game, **btn_cfg,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            controls, text="💡 Решить", bg="#9B59B6", fg="white",
            activebackground="#8E44AD", activeforeground="white",
            command=self._auto_solve, **btn_cfg,
        ).pack(side=tk.LEFT, padx=5)

        self.step_label = tk.Label(
            controls, text="", font=("Segoe UI", 11),
            bg=PANEL_COLOR, fg=TEXT_COLOR,
        )

        self.btn_back = tk.Button(
            controls, text="◀ Назад", bg="#E67E22", fg="white",
            activebackground="#D35400", activeforeground="white",
            command=self._solution_backward, **btn_cfg,
        )

        self.btn_forward = tk.Button(
            controls, text="Вперед ▶", bg="#27AE60", fg="white",
            activebackground="#229954", activeforeground="white",
            command=self._solution_forward, **btn_cfg,
        )

        self.peg_labels = ["A", "B", "C"]

    def _on_disk_change(self):
        try:
            val = self.disk_var.get()
            if 3 <= val <= 8:
                self.num_disks = val
                self._reset_game()
        except tk.TclError:
            pass

    def _reset_game(self):
        self.pegs = [list(range(self.num_disks, 0, -1)), [], []]
        self.moves = 0
        self.selected_peg = None
        self.animating = False
        self.solution_moves = []
        self.solution_idx = 0
        self.in_solution = False
        self._hide_solution_controls()
        self.min_moves = 2 ** self.num_disks - 1
        self.min_label.config(text=f"Минимум: {self.min_moves}")
        self.moves_label.config(text="Ходы: 0")
        self.status_label.config(text="Перенесите все диски на третий стержень", fg="#BDC3C7")
        self._draw()

    def _disk_width(self, size):
        ratio = (size - 1) / max(self.num_disks - 1, 1)
        return self.min_disk_width + ratio * (self.max_disk_width - self.min_disk_width)

    def _disk_color(self, size):
        idx = (size - 1) % len(DISK_COLORS)
        return DISK_COLORS[idx]

    def _lighter(self, hex_color, factor=0.3):
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darker(self, hex_color, factor=0.3):
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self):
        self.canvas.delete("all")

        shadow_pad = 6
        self.canvas.create_rectangle(
            20, self.base_y + 2, self.canvas_width - 20, self.base_y + 18 + shadow_pad,
            fill=SHADOW_COLOR, outline="",
        )

        self.canvas.create_rectangle(
            30, self.base_y, self.canvas_width - 30, self.base_y + 18,
            fill=BASE_COLOR, outline=self._darker(BASE_COLOR), width=2,
        )

        for i, x in enumerate(self.peg_x):
            peg_h = (self.num_disks + 1) * self.disk_height + 20
            peg_top = self.base_y - peg_h
            pw = 10

            self.canvas.create_rectangle(
                x - pw // 2 + 3, peg_top + 3,
                x + pw // 2 + 3, self.base_y,
                fill=SHADOW_COLOR, outline="",
            )

            outline = HIGHLIGHT_COLOR if self.selected_peg == i else self._darker(PEG_COLOR, 0.4)
            outline_w = 2 if self.selected_peg == i else 1
            self.canvas.create_rectangle(
                x - pw // 2, peg_top, x + pw // 2, self.base_y,
                fill=PEG_COLOR, outline=outline, width=outline_w,
            )

            highlight_x = x - pw // 2 + 2
            self.canvas.create_rectangle(
                highlight_x, peg_top, highlight_x + 3, self.base_y,
                fill=self._lighter(PEG_COLOR, 0.15), outline="",
            )

            self.canvas.create_text(
                x, self.base_y + 35,
                text=self.peg_labels[i],
                font=("Segoe UI", 13, "bold"), fill="#7F8C8D",
            )

        for peg_idx, peg in enumerate(self.pegs):
            x = self.peg_x[peg_idx]
            for slot, disk_size in enumerate(peg):
                w = self._disk_width(disk_size)
                color = self._disk_color(disk_size)
                y_top = self.base_y - (slot + 1) * self.disk_height

                is_top = (slot == len(peg) - 1) and (self.selected_peg == peg_idx)

                self.canvas.create_rectangle(
                    x - w / 2 + 3, y_top + 3,
                    x + w / 2 + 3, y_top + self.disk_height,
                    fill=SHADOW_COLOR, outline="",
                )

                outline_c = HIGHLIGHT_COLOR if is_top else self._darker(color, 0.3)
                outline_w = 2 if is_top else 1
                self.canvas.create_rectangle(
                    x - w / 2, y_top,
                    x + w / 2, y_top + self.disk_height,
                    fill=color, outline=outline_c, width=outline_w,
                )

                self.canvas.create_rectangle(
                    x - w / 2 + 4, y_top + 3,
                    x + w / 2 - 4, y_top + 7,
                    fill=self._lighter(color, 0.35), outline="",
                )

                self.canvas.create_rectangle(
                    x - w / 2 + 4, y_top + self.disk_height - 7,
                    x + w / 2 - 4, y_top + self.disk_height - 3,
                    fill=self._darker(color, 0.2), outline="",
                )

                self.canvas.create_text(
                    x, y_top + self.disk_height // 2,
                    text=str(disk_size),
                    font=("Segoe UI", 10, "bold"), fill="white",
                )

    def _peg_from_x(self, x):
        for i, px in enumerate(self.peg_x):
            if abs(x - px) < 100:
                return i
        return None

    def _on_click(self, event):
        if self.animating:
            return

        peg = self._peg_from_x(event.x)
        if peg is None:
            self.selected_peg = None
            self._draw()
            return

        if self.selected_peg is None:
            if self.pegs[peg]:
                self.selected_peg = peg
                self._draw()
            else:
                self.status_label.config(text="Этот стержень пуст!", fg="#E74C3C")
        else:
            if peg == self.selected_peg:
                self.selected_peg = None
                self._draw()
                return

            from_peg = self.pegs[self.selected_peg]
            to_peg = self.pegs[peg]

            if not from_peg:
                self.selected_peg = None
                self._draw()
                return

            disk = from_peg[-1]
            if not to_peg or disk < to_peg[-1]:
                to_peg.append(from_peg.pop())
                self.moves += 1
                self.moves_label.config(text=f"Ходы: {self.moves}")
                self.selected_peg = None
                self._draw()
                self._check_win()
            else:
                self.status_label.config(
                    text="Нельзя положить большой диск на маленький!", fg="#E74C3C",
                )
                self.selected_peg = None
                self._draw()

    def _check_win(self):
        if len(self.pegs[2]) == self.num_disks:
            if self.in_solution:
                self.status_label.config(text="🎉 Решение завершено!", fg=WIN_COLOR)
                return
            msg = f"Победа! Вы решили за {self.moves} ходов "
            msg += f"(минимум {self.min_moves})."
            if self.moves == self.min_moves:
                msg += "\n🌟 Идеальное решение!"
            self.status_label.config(text="🎉 Победа!", fg=WIN_COLOR)
            messagebox.showinfo("Победа!", msg)
            self.animating = True

    def _auto_solve(self):
        if self.animating and not self.in_solution:
            return
        self._reset_game()
        self.animating = True
        self.in_solution = True
        self.solution_moves = []
        self._gen_moves(self.num_disks, 0, 2, 1, self.solution_moves)
        self.solution_idx = 0
        self._show_solution_controls()
        self.status_label.config(text="Режим решения: листайте ходы", fg=MOVE_TEXT_COLOR)
        self._draw()

    def _gen_moves(self, n, src, dst, aux, moves):
        if n == 0:
            return
        self._gen_moves(n - 1, src, aux, dst, moves)
        moves.append((src, dst))
        self._gen_moves(n - 1, aux, dst, src, moves)

    def _show_solution_controls(self):
        self.step_label.pack(side=tk.LEFT, padx=10)
        self.btn_back.pack(side=tk.LEFT, padx=5)
        self.btn_forward.pack(side=tk.LEFT, padx=5)
        self._update_solution_ui()

    def _hide_solution_controls(self):
        self.step_label.pack_forget()
        self.btn_back.pack_forget()
        self.btn_forward.pack_forget()

    def _update_solution_ui(self):
        total = len(self.solution_moves)
        self.step_label.config(text=f"Шаг: {self.solution_idx}/{total}")
        self.btn_back.config(state=tk.NORMAL if self.solution_idx > 0 else tk.DISABLED)
        self.btn_forward.config(state=tk.NORMAL if self.solution_idx < total else tk.DISABLED)

    def _solution_forward(self):
        if not self.in_solution or self.solution_idx >= len(self.solution_moves):
            return
        src, dst = self.solution_moves[self.solution_idx]
        disk = self.pegs[src].pop()
        self.pegs[dst].append(disk)
        self.solution_idx += 1
        self.moves += 1
        self.moves_label.config(text=f"Ходы: {self.moves}")
        self._update_solution_ui()
        self._draw()
        if self.solution_idx == len(self.solution_moves):
            self._check_win()

    def _solution_backward(self):
        if not self.in_solution or self.solution_idx <= 0:
            return
        self.solution_idx -= 1
        self._apply_solution_state(self.solution_idx)
        self._update_solution_ui()

    def _apply_solution_state(self, target_idx):
        self.pegs = [list(range(self.num_disks, 0, -1)), [], []]
        for i in range(target_idx):
            src, dst = self.solution_moves[i]
            disk = self.pegs[src].pop()
            self.pegs[dst].append(disk)
        self.moves = target_idx
        self.moves_label.config(text=f"Ходы: {self.moves}")
        self._draw()


def main():
    root = tk.Tk()
    w, h = 920, 600
    sx = root.winfo_screenwidth() // 2 - w // 2
    sy = root.winfo_screenheight() // 2 - h // 2
    root.geometry(f"{w}x{h}+{sx}+{sy}")

    TowerOfHanoi(root)
    root.mainloop()


if __name__ == "__main__":
    main()
