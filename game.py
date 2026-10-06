import math
import random
from array import array

import pygame

pygame.init()

try:
    pygame.mixer.init()
    mixer_ready = True
except pygame.error:
    mixer_ready = False

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 680
BOARD_WIDTH = 600
BOARD_HEIGHT = 400
CELL_SIZE = 10
BOARD_X = 42
BOARD_Y = 190
PANEL_X = 682
PANEL_WIDTH = 236

BACKGROUND = (10, 15, 28)
SURFACE = (18, 26, 43)
SURFACE_LIGHT = (25, 36, 56)
BOARD_COLOR = (12, 20, 33)
GRID_COLOR = (23, 34, 51)
TEXT = (231, 239, 249)
MUTED = (137, 153, 174)
ACCENT = (67, 230, 190)
ACCENT_DARK = (33, 160, 139)
FOOD_COLOR = (255, 104, 137)
WARNING = (255, 190, 92)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Slither to Eat")
clock = pygame.time.Clock()

small_font = pygame.font.SysFont("segoeui", 16)
body_font = pygame.font.SysFont("segoeui", 20)
heading_font = pygame.font.SysFont("segoeui", 30, bold=True)
title_font = pygame.font.SysFont("segoeui", 56, bold=True)
score_font = pygame.font.SysFont("segoeui", 42, bold=True)

base_speed = 12
max_speed = 25
snake_speed = base_speed
best_score = 0


def make_tone(frequency, duration_ms=120, volume=0.10):
    if not mixer_ready:
        return None

    sample_rate = 22050
    total_samples = int(sample_rate * duration_ms / 1000)
    amplitude = int(32767 * volume)
    samples = array("h")
    for i in range(total_samples):
        wave = math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(int(wave * amplitude))
    return pygame.mixer.Sound(buffer=samples.tobytes())


eat_sound = make_tone(660, 90, 0.15)
death_sound = make_tone(180, 220, 0.2)


def play_sound(sound):
    if sound is not None:
        sound.play()


def draw_text(text, font, color, position, centered=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if centered:
        rect.center = position
    else:
        rect.topleft = position
    display.blit(image, rect)
    return rect


def draw_card(rect, color=SURFACE, radius=18, border=None):
    pygame.draw.rect(display, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(display, border, rect, width=1, border_radius=radius)


def draw_background():
    display.fill(BACKGROUND)
    pygame.draw.circle(display, (15, 39, 52), (WINDOW_WIDTH - 80, 65), 170)
    pygame.draw.circle(display, (15, 39, 52), (WINDOW_WIDTH - 80, 65), 170, 1)
    pygame.draw.circle(display, (16, 31, 49), (70, WINDOW_HEIGHT - 15), 150)


def draw_header():
    draw_text("SNAKE", heading_font, TEXT, (42, 30))
    draw_text("PUZZLE", heading_font, ACCENT, (150, 30))
    draw_text("SLITHER TO EAT", small_font, MUTED, (44, 70))
    pygame.draw.line(display, (37, 51, 70), (42, 112), (WINDOW_WIDTH - 42, 112), 1)
    draw_card(pygame.Rect(WINDOW_WIDTH - 190, 36, 148, 34), SURFACE_LIGHT, 17)
    pygame.draw.circle(display, ACCENT, (WINDOW_WIDTH - 170, 53), 4)
    draw_text("ARCADE MODE", small_font, MUTED, (WINDOW_WIDTH - 156, 43))


def draw_board(snake, food):
    board_rect = pygame.Rect(BOARD_X - 10, BOARD_Y - 10, BOARD_WIDTH + 20, BOARD_HEIGHT + 20)
    draw_card(board_rect, SURFACE, 20, (37, 51, 70))
    pygame.draw.rect(
        display,
        BOARD_COLOR,
        (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT),
        border_radius=10,
    )

    for x in range(0, BOARD_WIDTH + 1, CELL_SIZE * 2):
        pygame.draw.line(
            display,
            GRID_COLOR,
            (BOARD_X + x, BOARD_Y),
            (BOARD_X + x, BOARD_Y + BOARD_HEIGHT),
        )
    for y in range(0, BOARD_HEIGHT + 1, CELL_SIZE * 2):
        pygame.draw.line(
            display,
            GRID_COLOR,
            (BOARD_X, BOARD_Y + y),
            (BOARD_X + BOARD_WIDTH, BOARD_Y + y),
        )

    food_center = (BOARD_X + food[0] + CELL_SIZE // 2, BOARD_Y + food[1] + CELL_SIZE // 2)
    pygame.draw.circle(display, (87, 39, 68), food_center, 10)
    pygame.draw.circle(display, FOOD_COLOR, food_center, 5)
    pygame.draw.circle(display, (255, 210, 221), (food_center[0] - 1, food_center[1] - 1), 2)

    for index, segment in enumerate(reversed(snake)):
        color = ACCENT if index == len(snake) - 1 else (
            48 + min(index, 8) * 2,
            185 + min(index, 8) * 4,
            159 + min(index, 8) * 3,
        )
        segment_rect = pygame.Rect(
            BOARD_X + segment[0] + 1,
            BOARD_Y + segment[1] + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        pygame.draw.rect(display, color, segment_rect, border_radius=4)

    head = snake[0]
    head_rect = pygame.Rect(BOARD_X + head[0], BOARD_Y + head[1], CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(display, (153, 255, 226), head_rect, border_radius=4)


def draw_panel(score, speed, paused=False):
    score_rect = pygame.Rect(PANEL_X, BOARD_Y - 10, PANEL_WIDTH, 126)
    draw_card(score_rect)
    draw_text("YOUR SCORE", small_font, MUTED, (PANEL_X + 20, BOARD_Y + 10))
    draw_text(str(score).zfill(2), score_font, TEXT, (PANEL_X + 18, BOARD_Y + 34))
    pygame.draw.circle(display, ACCENT, (PANEL_X + PANEL_WIDTH - 25, BOARD_Y + 42), 5)
    draw_text("BEST", small_font, MUTED, (PANEL_X + 20, BOARD_Y + 89))
    draw_text(str(best_score), body_font, ACCENT, (PANEL_X + 76, BOARD_Y + 84))

    status_rect = pygame.Rect(PANEL_X, BOARD_Y + 130, PANEL_WIDTH, 70)
    draw_card(status_rect, SURFACE_LIGHT, 14)
    status_color = WARNING if paused else ACCENT
    status_text = "PAUSED" if paused else "IN PLAY"
    pygame.draw.circle(display, status_color, (PANEL_X + 23, BOARD_Y + 165), 5)
    draw_text(status_text, small_font, status_color, (PANEL_X + 38, BOARD_Y + 155))
    draw_text(f"SPEED  {speed}", small_font, MUTED, (PANEL_X + 134, BOARD_Y + 155))

    controls_rect = pygame.Rect(PANEL_X, BOARD_Y + 212, PANEL_WIDTH, 190)
    draw_card(controls_rect)
    draw_text("CONTROLS", small_font, MUTED, (PANEL_X + 20, BOARD_Y + 230))
    draw_text("Move", body_font, TEXT, (PANEL_X + 20, BOARD_Y + 260))
    draw_text("ARROWS  /  WASD", small_font, ACCENT, (PANEL_X + 20, BOARD_Y + 290))
    draw_text("Pause", body_font, TEXT, (PANEL_X + 20, BOARD_Y + 320))
    draw_text("SPACE", small_font, ACCENT, (PANEL_X + 20, BOARD_Y + 350))
    draw_text("Restart", body_font, TEXT, (PANEL_X + 128, BOARD_Y + 320))
    draw_text("R", small_font, ACCENT, (PANEL_X + 128, BOARD_Y + 350))


def draw_footer():
    draw_text("Eat the glowing fruit. Don't hit the walls or your tail.", small_font, MUTED, (42, 620))
    draw_text("Q  QUIT", small_font, MUTED, (WINDOW_WIDTH - 112, 620))


def spawn_food(snake):
    available = [
        [x, y]
        for x in range(0, BOARD_WIDTH, CELL_SIZE)
        for y in range(0, BOARD_HEIGHT, CELL_SIZE)
        if [x, y] not in snake
    ]
    return random.choice(available) if available else None


def reset_game():
    global snake_speed
    snake_speed = base_speed
    start_x = BOARD_WIDTH // 2
    start_y = BOARD_HEIGHT // 2
    snake = [
        [start_x, start_y],
        [start_x - CELL_SIZE, start_y],
        [start_x - 2 * CELL_SIZE, start_y],
    ]
    direction = [CELL_SIZE, 0]
    score = 0
    food = spawn_food(snake)
    return snake, direction, score, food


def start_screen():
    while True:
        draw_background()
        draw_header()
        draw_card(pygame.Rect(152, 165, 656, 390), SURFACE, 24, (37, 51, 70))
        draw_text("SLITHER", title_font, TEXT, (480, 245), centered=True)
        draw_text("TO EAT", title_font, ACCENT, (480, 303), centered=True)
        draw_text("A little bite-sized arcade challenge.", body_font, MUTED, (480, 375), centered=True)

        button = pygame.Rect(342, 425, 276, 56)
        draw_card(button, ACCENT_DARK, 16)
        draw_text("PRESS ENTER TO PLAY", small_font, TEXT, button.center, centered=True)
        draw_text("Arrow keys or WASD to steer  ·  Space to pause", small_font, MUTED, (480, 515), centered=True)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and button.collidepoint(event.pos):
                return True


def game_over_screen(score):
    global best_score
    best_score = max(best_score, score)

    while True:
        draw_background()
        draw_header()
        draw_card(pygame.Rect(192, 180, 576, 340), SURFACE, 24, (37, 51, 70))
        draw_text("RUN COMPLETE", heading_font, FOOD_COLOR, (480, 250), centered=True)
        draw_text(f"{score} POINTS", score_font, TEXT, (480, 315), centered=True)
        draw_text(f"PERSONAL BEST  {best_score}", small_font, ACCENT, (480, 370), centered=True)
        draw_text("Press R to play again  ·  Q to quit", body_font, MUTED, (480, 435), centered=True)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False


def render_game(snake, food, score, paused=False):
    draw_background()
    draw_header()
    draw_board(snake, food)
    draw_panel(score, snake_speed, paused)
    draw_footer()
    if paused:
        shade = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 9, 18, 170))
        display.blit(shade, (BOARD_X, BOARD_Y))
        draw_text("PAUSED", heading_font, TEXT, (BOARD_X + BOARD_WIDTH // 2, BOARD_Y + 170), centered=True)
        draw_text("Press SPACE to continue", small_font, MUTED, (BOARD_X + BOARD_WIDTH // 2, BOARD_Y + 210), centered=True)
    pygame.display.flip()


def game_loop():
    global snake_speed, best_score

    if not start_screen():
        pygame.quit()
        return

    snake, direction, score, food = reset_game()
    paused = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and direction != [CELL_SIZE, 0]:
                    direction = [-CELL_SIZE, 0]
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != [-CELL_SIZE, 0]:
                    direction = [CELL_SIZE, 0]
                elif event.key in (pygame.K_UP, pygame.K_w) and direction != [0, CELL_SIZE]:
                    direction = [0, -CELL_SIZE]
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != [0, -CELL_SIZE]:
                    direction = [0, CELL_SIZE]
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    snake, direction, score, food = reset_game()
                    paused = False
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        if not running:
            break

        if not paused:
            head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
            hit_wall = (
                head[0] < 0
                or head[0] >= BOARD_WIDTH
                or head[1] < 0
                or head[1] >= BOARD_HEIGHT
            )
            hit_tail = head in (snake[1:] if head == food else snake[1:-1])

            if hit_wall or hit_tail:
                play_sound(death_sound)
                best_score = max(best_score, score)
                if game_over_screen(score):
                    snake, direction, score, food = reset_game()
                    paused = False
                    continue
                running = False
                continue

            snake.insert(0, head)
            if head == food:
                play_sound(eat_sound)
                score += 1
                best_score = max(best_score, score)
                snake_speed = min(max_speed, base_speed + score // 3)
                food = spawn_food(snake)
                if food is None:
                    if game_over_screen(score):
                        snake, direction, score, food = reset_game()
                        continue
                    running = False
                    break
            else:
                snake.pop()

        render_game(snake, food, score, paused)
        clock.tick(snake_speed if not paused else 30)

    pygame.quit()


if __name__ == "__main__":
    game_loop()
