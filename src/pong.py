import pygame
pygame.init()

# -----------------------------
# Screen / timing
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Pong")
clock = pygame.time.Clock()
FPS = 60

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -----------------------------
# Game objects / constants
# -----------------------------
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 20

# Player movement speed
paddle_speed = 5

# Ball starting horizontal speed (vertical starts 0)
ball_speed_x, ball_speed_y = 4, 0
MAX_Y_SPEED = 7

# AI settings (smooth & beatable)
AI_SPEED = 4       # max pixels per frame the AI paddle can move
AI_MARGIN = 10     # dead zone in pixels around paddle center where AI doesn't react

# Player paddle (left)
left_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
# AI paddle (right)
right_paddle = pygame.Rect(WIDTH - 60, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
# Ball
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Scores and font
left_score = 0
right_score = 0
font = pygame.font.Font(None, 50)

# Cache score surfaces and update only when score changes
def make_score_surfaces():
    left_surf = font.render(str(left_score), True, WHITE)
    right_surf = font.render(str(right_score), True, WHITE)
    return left_surf, right_surf

left_score_surf, right_score_surf = make_score_surfaces()

# -----------------------------
# Paddle bounce (8-section) with clipping fix
# -----------------------------
def paddle_bounce(paddle):
    global ball_speed_x, ball_speed_y
    if ball.colliderect(paddle):
        section_height = paddle.height / 8.0
        hit_pos = int((ball.centery - paddle.top) // section_height)
        hit_pos = max(0, min(7, hit_pos))  # clamp

        # vertical speeds mapped to 8 sections (top -> bottom)
        bounce_speeds = [-6, -4, -2, -1, 1, 2, 4, 6]
        ball_speed_y = bounce_speeds[hit_pos]

        # reverse horizontal direction
        ball_speed_x *= -1

        # reposition ball to avoid clipping inside paddle
        if ball_speed_x > 0:  # now moving right
            ball.left = paddle.right
        else:
            ball.right = paddle.left

        # clamp vertical speed
        ball_speed_y = max(-MAX_Y_SPEED, min(MAX_Y_SPEED, ball_speed_y))

# -----------------------------
# Main loop
# -----------------------------
running = True
while running:
    # ---- events ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- input (player) ----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        left_paddle.y -= paddle_speed
    if keys[pygame.K_s]:
        left_paddle.y += paddle_speed

    # clamp player paddle inside screen
    left_paddle.top = max(0, left_paddle.top)
    left_paddle.bottom = min(HEIGHT, left_paddle.bottom)

    # ---- AI movement (smooth) ----
    # Move toward the ball smoothly, but only if ball center is outside AI_MARGIN
    diff = ball.centery - right_paddle.centery
    if abs(diff) > AI_MARGIN:
        # move at most AI_SPEED each frame toward the ball
        move = AI_SPEED if diff > 0 else -AI_SPEED
        # if diff is smaller than AI_SPEED, snap exactly to avoid overshoot
        if abs(diff) < AI_SPEED:
            right_paddle.y += diff
        else:
            right_paddle.y += move

    # clamp AI paddle inside screen
    right_paddle.top = max(0, right_paddle.top)
    right_paddle.bottom = min(HEIGHT, right_paddle.bottom)

    # ---- ball movement ----
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # ---- wall collisions (top/bottom) ----
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
        # ensure ball is inside usable area after bounce
        ball.top = max(0, ball.top)
        ball.bottom = min(HEIGHT, ball.bottom)

    # ---- paddle collisions ----
    paddle_bounce(left_paddle)
    paddle_bounce(right_paddle)

    # ---- scoring (left / right walls) ----
    score_changed = False
    if ball.left <= 0:
        right_score += 1
        score_changed = True
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = 4
        ball_speed_y = 0
    if ball.right >= WIDTH:
        left_score += 1
        score_changed = True
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = -4
        ball_speed_y = 0

    # update score surfaces only when score changed
    if score_changed:
        left_score_surf, right_score_surf = make_score_surfaces()

    # ---- drawing ----
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # draw scores (using cached surfaces)
    screen.blit(left_score_surf, (WIDTH // 4 - left_score_surf.get_width() // 2, 20))
    screen.blit(right_score_surf, (3 * WIDTH // 4 - right_score_surf.get_width() // 2, 20))

    # ---- update ----
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
