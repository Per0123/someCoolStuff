import pygame
import math

# =====================
# CONFIGURATION
# =====================
WIDTH, HEIGHT = 1200, 800
FPS = 60

G = 6.67430e-11        # Gravitational constant
DT = 3600              # Time step: 1 hour per update
SCALE = 1e9            # meters → pixels

# =====================
# BODY CLASS
# =====================
class Body:
    def __init__(self, x, y, vx, vy, mass, radius, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.mass = mass
        self.radius = radius
        self.color = color
        self.trail = []

# =====================
# PHYSICS
# =====================
def compute_gravity(bodies):
    for b in bodies:
        b.ax = 0
        b.ay = 0

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]

            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq)

            if dist == 0:
                continue

            force = G * b1.mass * b2.mass / dist_sq
            fx = force * dx / dist
            fy = force * dy / dist

            b1.ax += fx / b1.mass
            b1.ay += fy / b1.mass
            b2.ax -= fx / b2.mass
            b2.ay -= fy / b2.mass


def update(bodies, dt):
    # First half-step
    for b in bodies:
        b.vx += 0.5 * b.ax * dt
        b.vy += 0.5 * b.ay * dt
        b.x += b.vx * dt
        b.y += b.vy * dt

    compute_gravity(bodies)

    # Second half-step
    for b in bodies:
        b.vx += 0.5 * b.ax * dt
        b.vy += 0.5 * b.ay * dt

        # Save trail
        b.trail.append((b.x, b.y))
        if len(b.trail) > 300:
            b.trail.pop(0)

# =====================
# MAIN
# =====================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Planet Simulator (Realistic Gravity)")
clock = pygame.time.Clock()

# =====================
# CREATE BODIES
# =====================
bodies = [
    # Sun
    Body(
        x=0, y=0,
        vx=0, vy=0,
        mass=1.989e30,
        radius=10,
        color=(255, 255, 0)
    ),

    # Earth
    Body(
        x=1.496e11, y=0,
        vx=0, vy=29_780,
        mass=5.972e24,
        radius=5,
        color=(100, 150, 255)
    ),

    # Mars
    Body(
        x=2.279e11, y=0,
        vx=0, vy=24_070,
        mass=6.39e23,
        radius=4,
        color=(255, 100, 100)
    )
]

compute_gravity(bodies)

running = True
while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update(bodies, DT)

    # Draw trails
    for b in bodies:
        if len(b.trail) > 1:
            points = []
            for tx, ty in b.trail:
                px = WIDTH // 2 + int(tx / SCALE)
                py = HEIGHT // 2 + int(ty / SCALE)
                points.append((px, py))
            pygame.draw.lines(screen, b.color, False, points, 1)

    # Draw bodies
    for b in bodies:
        px = WIDTH // 2 + int(b.x / SCALE)
        py = HEIGHT // 2 + int(b.y / SCALE)
        pygame.draw.circle(screen, b.color, (px, py), b.radius)

    pygame.display.flip()

pygame.quit()
