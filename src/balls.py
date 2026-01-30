import pygame
import math
import random

# ------------------ SETUP ------------------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Ball Simulator")
clock = pygame.time.Clock()

GRAVITY = 1200
BOUNCE = 0.9
BG_COLOR = (25, 25, 30)

# ------------------ BALL CLASS ------------------
class Ball:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = radius * radius
        self.vx = 0
        self.vy = 0
        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def update(self, dt):
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.wall_collision()

    def wall_collision(self):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -BOUNCE

        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -BOUNCE

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -BOUNCE

        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -BOUNCE

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

# ------------------ COLLISIONS ------------------
def ball_collision(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.hypot(dx, dy)

    if dist == 0:
        return

    if dist < b1.radius + b2.radius:
        nx = dx / dist
        ny = dy / dist

        overlap = (b1.radius + b2.radius) - dist
        b1.x -= nx * overlap / 2
        b1.y -= ny * overlap / 2
        b2.x += nx * overlap / 2
        b2.y += ny * overlap / 2

        dvx = b2.vx - b1.vx
        dvy = b2.vy - b1.vy
        dot = dvx * nx + dvy * ny

        if dot > 0:
            return

        impulse = (2 * dot) / (b1.mass + b2.mass)
        b1.vx += impulse * b2.mass * nx
        b1.vy += impulse * b2.mass * ny
        b2.vx -= impulse * b1.mass * nx
        b2.vy -= impulse * b1.mass * ny

# ------------------ MAIN LOOP ------------------
balls = []
selected_ball = None
prev_mouse = (0, 0)

running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if event.button == 1:  # left click → drag
                for ball in reversed(balls):
                    if math.hypot(ball.x - mx, ball.y - my) < ball.radius:
                        selected_ball = ball
                        prev_mouse = (mx, my)
                        break

            if event.button == 3:  # right click → spawn
                balls.append(Ball(mx, my))

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and selected_ball:
                mx, my = pygame.mouse.get_pos()
                dx = mx - prev_mouse[0]
                dy = my - prev_mouse[1]
                selected_ball.vx = dx * 8
                selected_ball.vy = dy * 8
                selected_ball = None

    if selected_ball:
        mx, my = pygame.mouse.get_pos()
        selected_ball.x = mx
        selected_ball.y = my
        selected_ball.vx = 0
        selected_ball.vy = 0
        prev_mouse = (mx, my)

    for ball in balls:
        if ball != selected_ball:
            ball.update(dt)

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball_collision(balls[i], balls[j])

    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
