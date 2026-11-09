
import tkinter as tk
import time
import math


# =========================
# GAME CONFIGURATION
# =========================
WIDTH = 610
HEIGHT = 400
FPS = 60
FRAME_TIME = 1000 // FPS

BG = "#10152b"
CYAN = "#00e5ff"
WHITE = "#ffffff"


# =========================
# GAME OBJECT
# =========================
class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# =========================
# BALL
# =========================
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 9
        self.speed = 300
        self.dx = 0.65
        self.dy = -0.76

        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill=WHITE,
            outline=CYAN,
            width=2
        )

        super().__init__(canvas, item)

    def update(self, dt):
        x = self.dx * self.speed * dt
        y = self.dy * self.speed * dt

        self.move(x, y)

        coords = self.get_position()

        # Dinding kiri dan kanan
        if coords[0] <= 0:
            self.dx = abs(self.dx)
            self.move(-coords[0], 0)

        elif coords[2] >= WIDTH:
            self.dx = -abs(self.dx)
            self.move(WIDTH - coords[2], 0)

        # Dinding atas
        if coords[1] <= 0:
            self.dy = abs(self.dy)
            self.move(0, -coords[1])

    def bounce_paddle(self, paddle):
        ball = self.get_position()
        pad = paddle.get_position()

        ball_center = (ball[0] + ball[2]) / 2
        paddle_center = (pad[0] + pad[2]) / 2

        offset = (
            ball_center - paddle_center
        ) / (paddle.width / 2)

        # Membatasi sudut pantulan
        offset = max(-0.85, min(0.85, offset))

        self.dx = offset
        self.dy = -math.sqrt(1 - self.dx ** 2)

        # Menempatkan bola tepat di atas paddle
        self.canvas.coords(
            self.item,
            ball[0],
            pad[1] - self.radius * 2,
            ball[2],
            pad[1]
        )


# =========================
# PADDLE
# =========================
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 95
        self.height = 12
        self.speed = 480

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=CYAN,
            outline=WHITE,
            width=2
        )

        super().__init__(canvas, item)

    def update(self, direction, dt):
        coords = self.get_position()

        new_x = direction * self.speed * dt

        if coords[0] + new_x < 0:
            new_x = -coords[0]

        elif coords[2] + new_x > WIDTH:
            new_x = WIDTH - coords[2]

        self.move(new_x, 0)


# =========================
# BRICK
# =========================
class Brick(GameObject):
    COLORS = {
        1: "#ff4757",
        2: "#ffa502",
        3: "#2ed573"
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 70
        self.height = 19
        self.hits = hits

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=self.COLORS[hits],
            outline=WHITE,
            width=1,
            tags="brick"
        )

        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1

        if self.hits <= 0:
            self.delete()
            return True

        self.canvas.itemconfig(
            self.item,
            fill=self.COLORS[self.hits]
        )

        return False


# =========================
# GAME
# =========================
class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.width = WIDTH
        self.height = HEIGHT
        self.lives = 3
        self.running = False
        self.game_over = False

        self.keys = set()
        self.last_time = time.perf_counter()

        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack()
        self.pack()

        self.items = {}

        self.paddle = Paddle(
            self.canvas,
            WIDTH / 2,
            350
        )

        self.items[self.paddle.item] = self.paddle

        self.ball = None

        # Membuat balok
        for x in range(5, WIDTH - 5, 75):
            self.add_brick(x + 37.5, 60, 2)
            self.add_brick(x + 37.5, 85, 1)
            self.add_brick(x + 37.5, 110, 1)

        self.hud = self.canvas.create_text(
            60, 20,
            text="",
            fill=WHITE,
            font=("Arial", 14, "bold")
        )

        self.message = None

        # Kontrol keyboard
        self.canvas.focus_set()

        self.canvas.bind("<KeyPress>", self.key_down)
        self.canvas.bind("<KeyRelease>", self.key_up)

        self.master.bind("<FocusOut>", self.clear_keys)
        self.master.bind("<FocusIn>", self.restore_focus)

        self.setup_game()

    # =====================
    # KEYBOARD
    # =====================
    def key_down(self, event):
        key = event.keysym.lower()

        if key in ("left", "right", "a", "d"):
            self.keys.add(key)

        elif key == "space":
            if not self.running and not self.game_over:
                self.start_game()

            elif self.game_over:
                self.restart_game()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def clear_keys(self, event=None):
        self.keys.clear()

    def restore_focus(self, event=None):
        self.canvas.focus_set()

    # =====================
    # SETUP
    # =====================
    def setup_game(self):
        self.running = False
        self.last_time = time.perf_counter()

        self.add_ball()

        self.update_hud()

        self.show_message(
            "PRESS SPACE TO START",
            20
        )

    def add_ball(self):
        if self.ball:
            self.ball.delete()

        coords = self.paddle.get_position()

        x = (coords[0] + coords[2]) / 2

        self.ball = Ball(
            self.canvas,
            x,
            330
        )

    def add_brick(self, x, y, hits):
        brick = Brick(
            self.canvas,
            x,
            y,
            hits
        )

        self.items[brick.item] = brick

    # =====================
    # HUD
    # =====================
    def update_hud(self):
        self.canvas.itemconfig(
            self.hud,
            text=f"LIVES: {self.lives}"
        )

    def show_message(self, text, size):
        if self.message:
            self.canvas.delete(self.message)

        self.message = self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2,
            text=text,
            fill=CYAN,
            font=("Arial", size, "bold")
        )

    # =====================
    # START
    # =====================
    def start_game(self):
        if self.running:
            return

        self.running = True
        self.canvas.delete(self.message)
        self.message = None

        self.last_time = time.perf_counter()

        self.game_loop()

    # =====================
    # COLLISION
    # =====================
    def check_collisions(self):
        ball_coords = self.ball.get_position()

        overlapping = self.canvas.find_overlapping(
            *ball_coords
        )

        for item in overlapping:
            if item == self.ball.item:
                continue

            if item == self.paddle.item:
                ball = self.ball.get_position()
                paddle = self.paddle.get_position()

                if self.ball.dy > 0 and ball[3] >= paddle[1]:
                    self.ball.bounce_paddle(self.paddle)

                continue

            if item in self.items:
                obj = self.items[item]

                if isinstance(obj, Brick):
                    if self.ball.dy > 0:
                        self.ball.dy = -abs(self.ball.dy)
                    else:
                        self.ball.dy = abs(self.ball.dy)

                    destroyed = obj.hit()

                    if destroyed:
                        del self.items[item]

                    break

    # =====================
    # GAME LOOP
    # =====================
    def game_loop(self):
        if not self.running:
            return

        now = time.perf_counter()

        dt = min(now - self.last_time, 0.03)
        self.last_time = now

        # Paddle movement
        direction = 0

        if "left" in self.keys or "a" in self.keys:
            direction -= 1

        if "right" in self.keys or "d" in self.keys:
            direction += 1

        self.paddle.update(direction, dt)

        # Ball movement
        self.ball.update(dt)

        # Collision
        self.check_collisions()

        # Menang
        if not self.canvas.find_withtag("brick"):
            self.running = False
            self.show_message("YOU WIN!", 30)
            return

        # Kehilangan nyawa
        if self.ball.get_position()[3] >= HEIGHT:
            self.lives -= 1
            self.update_hud()

            self.running = False

            if self.lives <= 0:
                self.game_over = True
                self.show_message("GAME OVER!", 30)
                return

            self.canvas.after(800, self.setup_game)
            return

        # Loop berikutnya
        self.after(FRAME_TIME, self.game_loop)

    # =====================
    # RESTART
    # =====================
    def restart_game(self):
        self.running = False
        self.game_over = False
        self.lives = 3

        self.canvas.delete("all")
        self.items.clear()

        self.paddle = Paddle(
            self.canvas,
            WIDTH / 2,
            350
        )

        self.items[self.paddle.item] = self.paddle

        self.ball = None
        self.hud = self.canvas.create_text(
            60, 20,
            text="",
            fill=WHITE,
            font=("Arial", 14, "bold")
        )

        self.message = None

        for x in range(5, WIDTH - 5, 75):
            self.add_brick(x + 37.5, 60, 2)
            self.add_brick(x + 37.5, 85, 1)
            self.add_brick(x + 37.5, 110, 1)

        self.update_hud()
        self.setup_game()


# =========================
# MAIN PROGRAM
# =========================
if __name__ == "__main__":
    root = tk.Tk()

    root.title("Neon Brick Breaker")
    root.resizable(False, False)

    game = Game(root)

    game.mainloop()
