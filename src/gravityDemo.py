import pygame
import math
import random

# =====================
# SETTINGS
# =====================
WIDTH, HEIGHT = 1200, 800
FPS = 60

G = 9.8
DT = 0.1
BASE_MASS = 100  # Default mass for placable planets
SOFTENING = 0.1
MAX_TRAIL = 120
MAX_INITIAL_SPEED = 1  # Cap the initial placement speed

# =====================
# BODY
# =====================
class Body:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.mass = mass
        self.radius = int(math.sqrt(mass))
        self.trail = []
        # Random color for each planet
        self._color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def color(self):
        return self._color

    def update_radius(self):
        self.radius = max(2, int(math.sqrt(self.mass)))

# =====================
# TOROIDAL WRAP
# =====================
def wrap_position(b, world_w, world_h):
    wrapped = False
    if b.x < -world_w / 2:
        b.x += world_w
        wrapped = True
    elif b.x > world_w / 2:
        b.x -= world_w
        wrapped = True
    if b.y < -world_h / 2:
        b.y += world_h
        wrapped = True
    elif b.y > world_h / 2:
        b.y -= world_h
        wrapped = True
    if wrapped:
        b.trail.append(None)

# =====================
# GRAVITY
# =====================
def compute_gravity(bodies, world_w, world_h):
    for b in bodies:
        b.ax = 0
        b.ay = 0
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dx -= round(dx / world_w) * world_w
            dy -= round(dy / world_h) * world_h
            dist_sq = dx*dx + dy*dy + SOFTENING
            dist = math.sqrt(dist_sq)
            force = G * b1.mass * b2.mass / dist_sq
            fx = force * dx / dist
            fy = force * dy / dist
            b1.ax += fx / b1.mass
            b1.ay += fy / b1.mass
            b2.ax -= fx / b2.mass
            b2.ay -= fy / b2.mass

# =====================
# COLLISIONS WITH MERGING
# =====================
def handle_collisions(bodies, world_w, world_h):
    i = 0
    while i < len(bodies):
        b1 = bodies[i]
        j = i + 1
        while j < len(bodies):
            b2 = bodies[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dx -= round(dx / world_w) * world_w
            dy -= round(dy / world_h) * world_h
            dist = math.hypot(dx, dy)
            if dist < b1.radius + b2.radius:
                # Merge planets partially
                total_mass = b1.mass + b2.mass
                vx = (b1.vx * b1.mass + b2.vx * b2.mass) / total_mass
                vy = (b1.vy * b1.mass + b2.vy * b2.mass) / total_mass
                x = (b1.x * b1.mass + b2.x * b2.mass) / total_mass
                y = (b1.y * b1.mass + b2.y * b2.mass) / total_mass
                b1.x = x
                b1.y = y
                b1.vx = vx
                b1.vy = vy
                b1.mass = total_mass
                b1.update_radius()
                # merge trails
                b1.trail.extend(b2.trail)
                b1.trail = b1.trail[-MAX_TRAIL:]
                bodies.pop(j)
            else:
                j += 1
        i += 1

# =====================
# UPDATE
# =====================
def update(bodies, world_w, world_h):
    for b in bodies:
        b.vx += 0.5 * b.ax * DT
        b.vy += 0.5 * b.ay * DT
        b.x += b.vx * DT
        b.y += b.vy * DT
        wrap_position(b, world_w, world_h)
    compute_gravity(bodies, world_w, world_h)
    for b in bodies:
        b.vx += 0.5 * b.ax * DT
        b.vy += 0.5 * b.ay * DT
        b.trail.append((b.x, b.y))
        if len(b.trail) > MAX_TRAIL:
            b.trail.pop(0)
    handle_collisions(bodies, world_w, world_h)

# =====================
# ENERGY
# =====================
def total_energy(bodies, world_w, world_h):
    KE = sum(0.5*b.mass*(b.vx**2 + b.vy**2) for b in bodies)
    PE = 0
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            b1 = bodies[i]
            b2 = bodies[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dx -= round(dx / world_w) * world_w
            dy -= round(dy / world_h) * world_h
            dist = math.hypot(dx, dy) + SOFTENING
            PE -= G * b1.mass * b2.mass / dist
    return KE, PE, KE+PE

# =====================
# DRAW BODY WITH TOROIDAL RENDERING
# =====================
def draw_body_wrapped(screen, b):
    positions = []
    px = WIDTH//2 + int(b.x)
    py = HEIGHT//2 + int(b.y)
    positions.append((px, py))

    # horizontal wrapping
    if px - b.radius < 0:
        positions.append((px + WIDTH, py))
    if px + b.radius > WIDTH:
        positions.append((px - WIDTH, py))

    # vertical wrapping
    if py - b.radius < 0:
        positions.append((px, py + HEIGHT))
    if py + b.radius > HEIGHT:
        positions.append((px, py - HEIGHT))

    # diagonal corners
    if px - b.radius < 0 and py - b.radius < 0:
        positions.append((px + WIDTH, py + HEIGHT))
    if px - b.radius < 0 and py + b.radius > HEIGHT:
        positions.append((px + WIDTH, py - HEIGHT))
    if px + b.radius > WIDTH and py - b.radius < 0:
        positions.append((px - WIDTH, py + HEIGHT))
    if px + b.radius > WIDTH and py + b.radius > HEIGHT:
        positions.append((px - WIDTH, py - HEIGHT))

    for pos in positions:
        pygame.draw.circle(screen, b.color(), pos, max(2, b.radius))

# =====================
# MAIN
# =====================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Sandbox Colorful Planets")
clock = pygame.time.Clock()

bodies = []
dragging = False
start_pos = (0, 0)
paused = False

compute_gravity(bodies, WIDTH, HEIGHT)

running = True
while running:
    clock.tick(FPS)
    screen.fill((0,0,0))

    # =====================
    # EVENT HANDLING
    # =====================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Place planets
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            start_pos = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
            x0, y0 = start_pos
            x1, y1 = pygame.mouse.get_pos()
            x = x0 - WIDTH/2
            y = y0 - HEIGHT/2

            # --- SAFE INITIAL VELOCITY ---
            dx = x0 - x1
            dy = y0 - y1
            speed = math.hypot(dx, dy) * 0.05
            if speed > MAX_INITIAL_SPEED:
                scale = MAX_INITIAL_SPEED / speed
                dx *= scale
                dy *= scale
            vx = dx
            vy = dy
            # -----------------------------

            bodies.append(Body(x, y, vx, vy, BASE_MASS))
            compute_gravity(bodies, WIDTH, HEIGHT)

        # Pause / step
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_s and paused:
                update(bodies, WIDTH, HEIGHT)

    # =====================
    # PHYSICS UPDATE
    # =====================
    if not paused:
        update(bodies, WIDTH, HEIGHT)

    # =====================
    # DRAW TRAILS
    # =====================
    for b in bodies:
        segment = []
        for point in b.trail:
            if point is None:
                if len(segment) > 1:
                    pygame.draw.lines(screen, (120,120,160), False, segment, 1)
                segment = []
            else:
                x, y = point
                px = WIDTH//2 + int(x)
                py = HEIGHT//2 + int(y)
                segment.append((px, py))
        if len(segment) > 1:
            pygame.draw.lines(screen, (120,120,160), False, segment, 1)

    # =====================
    # DRAW BODIES
    # =====================
    for b in bodies:
        draw_body_wrapped(screen, b)

    # =====================
    # VELOCITY PREVIEW
    # =====================
    if dragging:
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255,100,100), start_pos, (mx,my), 2)

    # =====================
    # ENERGY DISPLAY
    # =====================
    KE, PE, TE = total_energy(bodies, WIDTH, HEIGHT)
    font = pygame.font.SysFont("Arial",16)
    info = font.render(f"KE: {KE:.2f} | PE: {PE:.2f} | TE: {TE:.2f} | Mass: {BASE_MASS}", True, (255,255,255))
    screen.blit(info, (10,10))

    pygame.display.flip()

pygame.quit()
