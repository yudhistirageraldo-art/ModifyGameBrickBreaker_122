
import pygame
import random
import math

pygame.init()

# =====================================
# CONFIGURATION
# =====================================

WIDTH, HEIGHT = 800, 600
FPS = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON BREAKER - Arcade Game")

clock = pygame.time.Clock()

# Colors
BG = (10, 10, 28)
WHITE = (245, 245, 255)
PURPLE = (160, 80, 255)
PINK = (255, 70, 180)
BLUE = (60, 180, 255)
CYAN = (50, 240, 230)
GREEN = (80, 255, 160)
RED = (255, 80, 100)

FONT = pygame.font.SysFont("arial", 20, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 15)

BLOCK_COLORS = [PURPLE, PINK, BLUE, CYAN, GREEN]

# =====================================
# BACKGROUND
# =====================================

stars = [
    (random.randint(0, WIDTH),
     random.randint(0, HEIGHT),
     random.randint(1, 2))
    for _ in range(90)
]


def draw_background():
    screen.fill(BG)

    for x, y, size in stars:
        pygame.draw.circle(
            screen,
            (55, 55, 100),
            (x, y),
            size
        )

    pygame.draw.line(
        screen,
        (50, 30, 90),
        (0, HEIGHT - 55),
        (WIDTH, HEIGHT - 55),
        2
    )


# GLOW EFFECT

def draw_glow(surface, color, center, radius):
    glow_surface = pygame.Surface(
        (radius * 4, radius * 4),
        pygame.SRCALPHA
    )

    for i in range(4, 0, -1):
        alpha = 15 * (5 - i)

        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (radius * 2, radius * 2),
            radius * i // 2
        )

    surface.blit(
        glow_surface,
        (
            center[0] - radius * 2,
            center[1] - radius * 2
        )
    )


# PARTICLES

particles = []


def create_particles(x, y, color):
    for _ in range(12):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-180, 180),
            "dy": random.uniform(-180, 180),
            "life": 0.5,
            "color": color
        })


def update_particles(dt):
    for p in particles[:]:
        p["x"] += p["dx"] * dt
        p["y"] += p["dy"] * dt
        p["life"] -= dt

        if p["life"] <= 0:
            particles.remove(p)
            continue

        pygame.draw.circle(
            screen,
            p["color"],
            (int(p["x"]), int(p["y"])),
            max(1, int(p["life"] * 6))
        )

# STRIKER / PADDLE

class Striker:

    def __init__(self):
        self.width = 120
        self.height = 16

        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 85

        self.speed = 540

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def update(self, direction, dt):
        self.x += direction * self.speed * dt

        self.x = max(
            10,
            min(WIDTH - self.width - 10, self.x)
        )

        self.rect.x = round(self.x)

    def display(self):
        draw_glow(
            screen,
            PURPLE,
            self.rect.center,
            35
        )

        pygame.draw.rect(
            screen,
            PURPLE,
            self.rect,
            border_radius=10
        )

        inner = self.rect.inflate(-8, -6)

        pygame.draw.rect(
            screen,
            (225, 195, 255),
            inner,
            border_radius=7
        )

# BALL

class Ball:

    def __init__(self):
        self.radius = 9
        self.speed = 360

        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 110

        self.dx = random.choice([-1, 1])
        self.dy = -1

        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self, dt):
        old_rect = self.rect.copy()

        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        # Left wall
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx = abs(self.dx)

        # Right wall
        if self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dx = -abs(self.dx)

        # Top wall
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy = abs(self.dy)

        self.rect.center = (
            round(self.x),
            round(self.y)
        )

        lost = self.y - self.radius >= HEIGHT

        return lost, old_rect

    def display(self):
        draw_glow(
            screen,
            CYAN,
            (round(self.x), round(self.y)),
            25
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (round(self.x), round(self.y)),
            self.radius
        )


# =====================================
# BLOCKS
# =====================================

class Block:

    def __init__(self, x, y, color):
        self.rect = pygame.Rect(
            x, y, 65, 24
        )

        self.color = color

        self.health = 2 if color == PURPLE else 1

    def display(self):
        if self.health <= 0:
            return

        draw_glow(
            screen,
            self.color,
            self.rect.center,
            15
        )

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=6
        )

        highlight = self.rect.inflate(-6, -12)

        pygame.draw.rect(
            screen,
            WHITE,
            highlight,
            border_radius=4
        )

    def hit(self):
        self.health -= 1


def create_blocks():
    blocks = []

    for row in range(5):
        for col in range(9):

            x = 30 + col * 82
            y = 85 + row * 42

            color = BLOCK_COLORS[row]

            blocks.append(
                Block(x, y, color)
            )

    return blocks


# HUD

def draw_hud(score, lives):

    pygame.draw.rect(
        screen,
        (24, 20, 48),
        (20, 15, WIDTH - 40, 48),
        border_radius=12
    )

    title = FONT.render(
        "NEON BREAKER", True, CYAN
    )

    score_text = FONT.render(
        f"SCORE : {score}", True, WHITE
    )

    lives_text = FONT.render(
        f"LIVES : {lives}", True, PINK
    )

    screen.blit(title, (35, 27))
    screen.blit(score_text, (340, 27))
    screen.blit(lives_text, (650, 27))


# GAME SCREEN

def draw_center_text(title, subtitle):

    title_surface = BIG_FONT.render(
        title, True, CYAN
    )

    subtitle_surface = FONT.render(
        subtitle, True, WHITE
    )

    screen.blit(
        title_surface,
        title_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 35)
        )
    )

    screen.blit(
        subtitle_surface,
        subtitle_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 25)
        )
    )

# MAIN GAME

def main():

    running = True

    score = 0
    lives = 3

    striker = Striker()
    ball = Ball()

    blocks = create_blocks()

    game_state = "START"
    direction = 0

    while running:

        # Calculate delta time
        dt = min(clock.tick(FPS) / 1000, 0.03)

        draw_background()

        # =================================
        # EVENT HANDLING
        # =================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_LEFT:
                    direction = -1

                if event.key == pygame.K_RIGHT:
                    direction = 1

                if event.key == pygame.K_SPACE:

                    if game_state in (
                        "START", "GAMEOVER", "WIN"
                    ):

                        score = 0
                        lives = 3

                        striker = Striker()
                        ball = Ball()

                        blocks = create_blocks()
                        particles.clear()

                        game_state = "PLAYING"

                    elif game_state == "PAUSED":
                        game_state = "PLAYING"

                if event.key == pygame.K_p:

                    if game_state == "PLAYING":
                        game_state = "PAUSED"

                    elif game_state == "PAUSED":
                        game_state = "PLAYING"

            if event.type == pygame.KEYUP:

                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT
                ):
                    direction = 0

        # =================================
        # PLAYING
        # =================================

        if game_state == "PLAYING":

            # Update striker
            striker.update(direction, dt)

            # Update ball
            lost, old_ball_rect = ball.update(dt)

            if lost:

                lives -= 1
                ball.reset()

                if lives <= 0:
                    game_state = "GAMEOVER"

            # Paddle collision
            if ball.rect.colliderect(striker.rect):

                if (
                    ball.dy > 0
                    and old_ball_rect.bottom <= striker.rect.top + 5
                ):

                    ball.dy = -1

                    hit_position = (
                        ball.x - striker.rect.centerx
                    ) / (striker.width / 2)

                    ball.dx = max(
                        -1,
                        min(1, hit_position)
                    )

                    if abs(ball.dx) < 0.25:
                        ball.dx = 0.25

                    ball.y = striker.y - ball.radius - 1

                    ball.rect.center = (
                        round(ball.x),
                        round(ball.y)
                    )

            # Block collision
            for block in blocks[:]:

                if ball.rect.colliderect(block.rect):

                    block.hit()

                    if old_ball_rect.bottom <= block.rect.top:
                        ball.dy = -abs(ball.dy)

                    elif old_ball_rect.top >= block.rect.bottom:
                        ball.dy = abs(ball.dy)

                    elif (
                        old_ball_rect.right <= block.rect.left
                        or old_ball_rect.left >= block.rect.right
                    ):
                        ball.dx *= -1

                    else:
                        ball.dy *= -1

                    if block.health <= 0:

                        create_particles(
                            block.rect.centerx,
                            block.rect.centery,
                            block.color
                        )

                        blocks.remove(block)
                        score += 10

                    break

            # Win condition
            if not blocks:
                game_state = "WIN"

        # DISPLAY

        draw_hud(score, lives)

        for block in blocks:
            block.display()

        if game_state in ("PLAYING", "PAUSED"):
            striker.display()
            ball.display()

        update_particles(dt)

        # Pause
        if game_state == "PAUSED":

            draw_center_text(
                "PAUSED",
                "PRESS SPACE OR P TO RESUME"
            )

        # Game Over
        elif game_state == "GAMEOVER":

            draw_center_text(
                "GAME OVER",
                f"FINAL SCORE: {score} | PRESS SPACE"
            )

        # Win
        elif game_state == "WIN":

            draw_center_text(
                "YOU WIN!",
                f"FINAL SCORE: {score} | PRESS SPACE"
            )

        # Start
        elif game_state == "START":

            draw_center_text(
                "NEON BREAKER",
                "PRESS SPACE TO START"
            )

        # Footer
        footer = SMALL_FONT.render(
            "ARROW KEYS: MOVE     P: PAUSE     ESC: QUIT",
            True,
            (130, 130, 170)
        )

        screen.blit(
            footer,
            footer.get_rect(
                center=(WIDTH // 2, HEIGHT - 25)
            )
        )

        pygame.display.flip()

    pygame.quit()

# RUN GAME

if __name__ == "__main__":
    main()
