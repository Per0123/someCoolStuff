import pygame
import math

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ---------- MAP ----------
WORLD_MAP = [
    "111111111111",
    "100000000001",
    "100000011111",
    "100110000000",
    "100110000000",
    "100000000000",
    "100000010001",
    "101110010001",
    "101010010001",
    "100010000001",
    "111111111111"
]

MAP_W = len(WORLD_MAP[0])
MAP_H = len(WORLD_MAP)

# ---------- CONSTANTS ----------
TILE = 64
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2   # faster
EPS = 1e-6

# ---------- PLAYER ----------
px, py = 150, 150
pa = 0.0
SPEED = 3
ROT = 0.04

# ---------- RAYCAST ----------
def cast_rays():
    start_angle = pa - HALF_FOV

    for ray in range(NUM_RAYS):
        angle = start_angle + ray * FOV / NUM_RAYS
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        map_x = int(px // TILE)
        map_y = int(py // TILE)

        step_x = 1 if cos_a > 0 else -1
        step_y = 1 if sin_a > 0 else -1

        cos_a = cos_a if abs(cos_a) > EPS else EPS
        sin_a = sin_a if abs(sin_a) > EPS else EPS

        delta_x = abs(TILE / cos_a)
        delta_y = abs(TILE / sin_a)

        if step_x > 0:
            side_x = ((map_x + 1) * TILE - px) / cos_a
        else:
            side_x = (px - map_x * TILE) / -cos_a

        if step_y > 0:
            side_y = ((map_y + 1) * TILE - py) / sin_a
        else:
            side_y = (py - map_y * TILE) / -sin_a

        for _ in range(64):
            # ✅ choose closest side FIRST
            if side_x < side_y:
                depth = side_x
                side_x += delta_x
                map_x += step_x
            else:
                depth = side_y
                side_y += delta_y
                map_y += step_y

            if not (0 <= map_x < MAP_W and 0 <= map_y < MAP_H):
                break

            if WORLD_MAP[map_y][map_x] == "1":
                depth *= math.cos(pa - angle)  # fish-eye fix
                wall_h = 30000 / (depth + 0.0001)

                shade = int(255 / (1 + depth * depth * 0.0001))
                x = ray * 2

                pygame.draw.rect(
                    screen,
                    (shade, shade, shade),
                    (x, HEIGHT // 2 - wall_h // 2, 2, wall_h)
                )
                break

# ---------- MAIN LOOP ----------
running = True
while running:
    screen.fill((70, 70, 70))                     # ceiling
    pygame.draw.rect(screen, (40, 40, 40),
                     (0, HEIGHT // 2, WIDTH, HEIGHT // 2))  # floor

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        pa -= ROT
    if keys[pygame.K_d]:
        pa += ROT
    if keys[pygame.K_w]:
        px += SPEED * math.cos(pa)
        py += SPEED * math.sin(pa)
    if keys[pygame.K_s]:
        px -= SPEED * math.cos(pa)
        py -= SPEED * math.sin(pa)

    cast_rays()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
