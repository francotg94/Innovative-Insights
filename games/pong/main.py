import sys
import tkinter as tk
from dataclasses import dataclass
from typing import Tuple

try:
    from . import config as cfg  # Run via module: python -m games.pong.main
except Exception:
    # Allow running as a script: python games/pong/main.py
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import config as cfg


@dataclass
class Paddle:
    x: int
    y: int
    w: int = cfg.PADDLE_WIDTH
    h: int = cfg.PADDLE_HEIGHT
    color: str = cfg.ACCENT_COLOR
    vy: int = 0

    def rect(self) -> Tuple[int, int, int, int]:
        return (self.x - self.w // 2, self.y - self.h // 2, self.x + self.w // 2, self.y + self.h // 2)

    def move(self, height: int, speed: int):
        self.y += self.vy * speed
        top = self.h // 2
        bottom = height - self.h // 2
        self.y = max(top, min(bottom, self.y))


@dataclass
class Ball:
    x: float
    y: float
    r: int = cfg.BALL_SIZE // 2
    vx: float = cfg.BALL_SPEED
    vy: float = cfg.BALL_SPEED * 0.4
    color: str = cfg.ACCENT2_COLOR

    def bbox(self) -> Tuple[int, int, int, int]:
        return (int(self.x - self.r), int(self.y - self.r), int(self.x + self.r), int(self.y + self.r))


class Game:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Innovative Insights Pong")
        self.root.configure(bg=cfg.BG_COLOR)
        self.root.geometry(f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}")
        self.root.minsize(700, 450)
        self.root.bind("<Escape>", lambda e: self.quit())
        self.root.bind("q", lambda e: self.quit())
        self.root.bind("Q", lambda e: self.quit())

        self.fullscreen = False
        self.root.bind("f", self.toggle_fullscreen)
        self.root.bind("F", self.toggle_fullscreen)

        self.canvas = tk.Canvas(
            self.root,
            width=cfg.WINDOW_WIDTH,
            height=cfg.WINDOW_HEIGHT,
            bg=cfg.BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        self.mode_single_player = True  # default to single-player vs AI
        self.score_left = 0
        self.score_right = 0
        self.win_score = cfg.WIN_SCORE
        self.paused = False
        self.showing_menu = True

        # Input
        self.root.bind("<KeyPress>", self.on_key_down)
        self.root.bind("<KeyRelease>", self.on_key_up)

        # Entities
        w = self.canvas.winfo_width() or cfg.WINDOW_WIDTH
        h = self.canvas.winfo_height() or cfg.WINDOW_HEIGHT
        self.left = Paddle(cfg.PADDLE_MARGIN, h // 2)
        self.right = Paddle(w - cfg.PADDLE_MARGIN, h // 2, color=cfg.ACCENT2_COLOR)
        self.ball = Ball(w // 2, h // 2)

        # Draw ids
        self.ids = {}

        # Menu bindings
        self.root.bind("1", lambda e: self.set_mode(single=True))
        self.root.bind("2", lambda e: self.set_mode(single=False))
        self.root.bind("p", lambda e: self.toggle_pause())
        self.root.bind("P", lambda e: self.toggle_pause())
        self.root.bind("r", lambda e: self.restart_round())
        self.root.bind("R", lambda e: self.restart_round())

        self.loop()

    # ------------ UI and Events ------------
    def on_resize(self, event):
        # Keep paddles at margins on resize
        self.right.x = event.width - cfg.PADDLE_MARGIN
        # Clamp paddles
        self.left.y = max(self.left.h // 2, min(event.height - self.left.h // 2, self.left.y))
        self.right.y = max(self.right.h // 2, min(event.height - self.right.h // 2, self.right.y))

    def toggle_fullscreen(self, _evt=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def quit(self):
        self.root.destroy()
        sys.exit(0)

    def set_mode(self, single: bool):
        self.mode_single_player = single
        self.showing_menu = False
        self.restart_round(center_only=True)

    def toggle_pause(self):
        self.paused = not self.paused

    def restart_round(self, center_only: bool = False):
        w = self.canvas.winfo_width() or cfg.WINDOW_WIDTH
        h = self.canvas.winfo_height() or cfg.WINDOW_HEIGHT
        self.ball.x, self.ball.y = w / 2, h / 2
        self.ball.vx = cfg.BALL_SPEED * (-1 if self.score_left <= self.score_right else 1)
        self.ball.vy = cfg.BALL_SPEED * 0.4
        if not center_only:
            self.left.y = h // 2
            self.right.y = h // 2

    def on_key_down(self, event):
        key = event.keysym
        if key in ("w", "W"):
            self.left.vy = -1
        elif key in ("s", "S"):
            self.left.vy = 1
        elif key == "Up":
            self.right.vy = -1
        elif key == "Down":
            self.right.vy = 1

    def on_key_up(self, event):
        key = event.keysym
        if key in ("w", "W", "s", "S"):
            self.left.vy = 0
        elif key in ("Up", "Down"):
            self.right.vy = 0

    # ------------ Game Loop ------------
    def loop(self):
        self.update()
        self.draw()
        self.root.after(int(1000 / cfg.FPS), self.loop)

    def update(self):
        w = self.canvas.winfo_width() or cfg.WINDOW_WIDTH
        h = self.canvas.winfo_height() or cfg.WINDOW_HEIGHT
        if self.showing_menu or self.paused:
            return

        # Move paddles
        self.left.move(h, cfg.PADDLE_SPEED)

        if self.mode_single_player:
            # Simple AI: track ball with capped speed
            target = self.ball.y
            if abs(self.right.y - target) > cfg.AI_PADDLE_SPEED:
                self.right.y += cfg.AI_PADDLE_SPEED if target > self.right.y else -cfg.AI_PADDLE_SPEED
        else:
            self.right.move(h, cfg.PADDLE_SPEED)

        # Move ball
        self.ball.x += self.ball.vx
        self.ball.y += self.ball.vy

        # Wall collisions
        if self.ball.y - self.ball.r <= 0 and self.ball.vy < 0:
            self.ball.vy *= -1
            self.root.bell()
        elif self.ball.y + self.ball.r >= h and self.ball.vy > 0:
            self.ball.vy *= -1
            self.root.bell()

        # Paddle collisions
        # Left paddle
        l = self.left
        if (self.ball.x - self.ball.r <= l.x + l.w // 2 and self.ball.x > l.x) and (l.y - l.h // 2 <= self.ball.y <= l.y + l.h // 2) and self.ball.vx < 0:
            self.ball.vx *= -1
            self.add_spin(l)
            self.speed_up_ball()
            self.root.bell()

        # Right paddle
        r = self.right
        if (self.ball.x + self.ball.r >= r.x - r.w // 2 and self.ball.x < r.x) and (r.y - r.h // 2 <= self.ball.y <= r.y + r.h // 2) and self.ball.vx > 0:
            self.ball.vx *= -1
            self.add_spin(r)
            self.speed_up_ball()
            self.root.bell()

        # Scoring
        if self.ball.x < -self.ball.r:
            self.score_right += 1
            self.check_win()
            self.restart_round()
        elif self.ball.x > w + self.ball.r:
            self.score_left += 1
            self.check_win()
            self.restart_round()

    def add_spin(self, paddle: Paddle):
        # Add vertical velocity based on collision offset
        offset = (self.ball.y - paddle.y) / (paddle.h / 2)
        self.ball.vy += offset * 2.0

    def speed_up_ball(self):
        import math

        speed = math.hypot(self.ball.vx, self.ball.vy) + cfg.BALL_SPEED_INC
        speed = min(speed, cfg.BALL_MAX_SPEED)
        ang = math.atan2(self.ball.vy, self.ball.vx)
        self.ball.vx = speed * math.cos(ang)
        self.ball.vy = speed * math.sin(ang)

    def check_win(self):
        if self.score_left >= self.win_score or self.score_right >= self.win_score:
            self.paused = True
            self.showing_menu = True
            self.score_left = 0
            self.score_right = 0

    # ------------ Drawing ------------
    def draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or cfg.WINDOW_WIDTH
        h = self.canvas.winfo_height() or cfg.WINDOW_HEIGHT

        # Center line
        self.canvas.create_line(w // 2, 0, w // 2, h, fill="#1f2937", dash=(8, 8))

        # Scores
        self.canvas.create_text(
            w * 0.25,
            40,
            text=str(self.score_left),
            fill=cfg.FG_COLOR,
            font=("SF Pro Display", 28, "bold"),
        )
        self.canvas.create_text(
            w * 0.75,
            40,
            text=str(self.score_right),
            fill=cfg.FG_COLOR,
            font=("SF Pro Display", 28, "bold"),
        )

        # Paddles and ball
        self.canvas.create_rectangle(*self.left.rect(), fill=self.left.color, width=0)
        self.canvas.create_rectangle(*self.right.rect(), fill=self.right.color, width=0)
        self.canvas.create_oval(*self.ball.bbox(), fill=self.ball.color, width=0)

        # Overlay menu or paused
        if self.showing_menu:
            self.draw_menu_overlay(w, h)
        elif self.paused:
            self.draw_paused_overlay(w, h)

    def draw_menu_overlay(self, w: int, h: int):
        self.canvas.create_rectangle(0, 0, w, h, fill=cfg.BG_COLOR, stipple="gray25", outline="")
        self.canvas.create_text(
            w // 2,
            h // 2 - 70,
            text="PONG",
            fill=cfg.FG_COLOR,
            font=("SF Pro Display", 48, "bold"),
        )
        self.canvas.create_text(
            w // 2,
            h // 2 - 20,
            text="1: Single-player  •  2: Two-player",
            fill=cfg.FG_COLOR,
            font=("SF Pro Text", 18),
        )
        self.canvas.create_text(
            w // 2,
            h // 2 + 20,
            text="Controls: W/S and ↑/↓  |  P: Pause  |  R: Restart",
            fill="#94a3b8",
            font=("SF Pro Text", 14),
        )
        self.canvas.create_text(
            w // 2,
            h // 2 + 50,
            text="F: Full-screen  •  Q/Esc: Quit",
            fill="#94a3b8",
            font=("SF Pro Text", 14),
        )

    def draw_paused_overlay(self, w: int, h: int):
        self.canvas.create_rectangle(0, 0, w, h, fill=cfg.BG_COLOR, stipple="gray25", outline="")
        self.canvas.create_text(
            w // 2,
            h // 2,
            text="Paused — press P to resume",
            fill=cfg.FG_COLOR,
            font=("SF Pro Display", 24, "bold"),
        )


def main():
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
