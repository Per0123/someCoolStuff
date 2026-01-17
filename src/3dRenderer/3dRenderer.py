import pygame
import math

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3dRenderer")
clock = pygame.time.Clock()

# ---------- MAP ----------
WORLD_MAP = [
    "111111111111",
    "100000000001",
    "100000011111",
    "100110000000",
    "100110000000",
    "100000000001",
    "100000010001",
    "100000010001",
    "101100010001",
    "100100000001",
    "111111111111"
]
MAP_W = len(WORLD_MAP[0])
MAP_H = len(WORLD_MAP)

# ---------- CONSTANTS ----------
TILE = 32
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
EPS = 1e-6

# Mini-map settings
MINIMAP_SCALE = 8  # smaller squares
MINIMAP_POS = (10, 10)  # top-left corner

# ---------- PLAYER ----------
px, py = 150, 150
pa = 0.0
SPEED = 1.5
ROT = 0.04

# ---------- TEXTURE ----------
wall_texture = pygame.image.load("wall.png").convert()

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
            if side_x < side_y:
                depth = side_x
                side_x += delta_x
                map_x += step_x
                hit_vertical = True
            else:
                depth = side_y
                side_y += delta_y
                map_y += step_y
                hit_vertical = False

            if not (0 <= map_x < MAP_W and 0 <= map_y < MAP_H):
                break

            if WORLD_MAP[map_y][map_x] == "1":
                # fish-eye correction
                depth *= math.cos(pa - angle)
                wall_h = 30000 / (depth + 0.0001)

                # Correct texture coordinate
                if hit_vertical:
                    hit_pos = py + depth * sin_a
                else:
                    hit_pos = px + depth * cos_a

                hit_pos %= TILE
                tex_x = min(int(hit_pos / TILE * wall_texture.get_width()),
                            wall_texture.get_width() - 1)

                column = wall_texture.subsurface(tex_x, 0, 1, wall_texture.get_height())
                column = pygame.transform.scale(column, (2, int(wall_h)))
                screen.blit(column, (ray * 2, HEIGHT // 2 - wall_h // 2))
                break

# ---------- MINI-MAP ----------
def draw_minimap():
    for y in range(MAP_H):
        for x in range(MAP_W):
            color = (200, 200, 200) if WORLD_MAP[y][x] == "1" else (30, 30, 30)
            rect = pygame.Rect(
                MINIMAP_POS[0] + x * MINIMAP_SCALE,
                MINIMAP_POS[1] + y * MINIMAP_SCALE,
                MINIMAP_SCALE,
                MINIMAP_SCALE
            )
            pygame.draw.rect(screen, color, rect)

    # Draw player on minimap
    player_rect = pygame.Rect(
        MINIMAP_POS[0] + px / TILE * MINIMAP_SCALE - 2,
        MINIMAP_POS[1] + py / TILE * MINIMAP_SCALE - 2,
        4,
        4
    )
    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    # Draw direction line
    end_x = MINIMAP_POS[0] + (px + math.cos(pa) * 20) / TILE * MINIMAP_SCALE
    end_y = MINIMAP_POS[1] + (py + math.sin(pa) * 20) / TILE * MINIMAP_SCALE
    pygame.draw.line(screen, (0, 255, 0),
                     (MINIMAP_POS[0] + px / TILE * MINIMAP_SCALE,
                      MINIMAP_POS[1] + py / TILE * MINIMAP_SCALE),
                     (end_x, end_y), 2)

# ---------- MAIN LOOP ----------
running = True
while running:
    screen.fill((100, 100, 100))  # ceiling
    pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))  # floor

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
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
    draw_minimap()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
