# ===================== IMPORTS =====================
import pygame
import random
import sys

# ===================== INIT =====================
pygame.init()

# ===================== SETTINGS =====================
WIDTH = 600
HEIGHT = 400
CELL = 20

FPS = 10
LEVEL = 1
SCORE = 0

# ===================== COLORS =====================
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# ===================== DISPLAY =====================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake PRO")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 50)

# ===================== SNAKE =====================
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL, 0)

# ===================== WALLS =====================
walls = []

def generate_walls(level):
    """Создание стен в зависимости от уровня"""
    walls.clear()

    # базовые стены (рамка)
    for x in range(0, WIDTH, CELL):
        walls.append((x, 0))
        walls.append((x, HEIGHT - CELL))

    for y in range(0, HEIGHT, CELL):
        walls.append((0, y))
        walls.append((WIDTH - CELL, y))

    # дополнительные стены с уровнем
    if level >= 2:
        for x in range(200, 400, CELL):
            walls.append((x, 200))

    if level >= 3:
        for y in range(100, 300, CELL):
            walls.append((300, y))

generate_walls(LEVEL)

# ===================== FOOD =====================
def generate_food():
    """Генерация еды НЕ на змее и НЕ на стене"""
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)

        if (x, y) not in snake and (x, y) not in walls:
            return (x, y)

food = generate_food()

# ===================== GAME OVER =====================
def game_over():
    """Экран Game Over"""
    screen.fill(BLACK)

    text1 = big_font.render("GAME OVER", True, RED)
    text2 = font.render(f"Score: {SCORE}", True, WHITE)
    text3 = font.render(f"Level: {LEVEL}", True, WHITE)

    screen.blit(text1, (150, 150))
    screen.blit(text2, (230, 230))
    screen.blit(text3, (230, 260))

    pygame.display.flip()
    pygame.time.delay(3000)

    pygame.quit()
    sys.exit()

# ===================== GAME LOOP =====================
while True:

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # управление
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL):
                direction = (0, -CELL)
            if event.key == pygame.K_DOWN and direction != (0, -CELL):
                direction = (0, CELL)
            if event.key == pygame.K_LEFT and direction != (CELL, 0):
                direction = (-CELL, 0)
            if event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                direction = (CELL, 0)

    # -------- MOVE --------
    head_x = snake[0][0] + direction[0]
    head_y = snake[0][1] + direction[1]
    new_head = (head_x, head_y)

    # -------- COLLISIONS --------
    # столкновение со стеной
    if new_head in walls:
        game_over()

    # выход за границы (доп защита)
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        game_over()

    # столкновение с собой
    if new_head in snake:
        game_over()

    snake.insert(0, new_head)

    # -------- FOOD --------
    if new_head == food:
        SCORE += 1

        # каждые 3 очка → новый уровень
        if SCORE % 3 == 0:
            LEVEL += 1
            FPS += 2
            generate_walls(LEVEL)

        food = generate_food()
    else:
        snake.pop()

    # -------- DRAW --------
    screen.fill(BLACK)

    # змейка
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL, CELL))

    # еда
    pygame.draw.rect(screen, RED, (*food, CELL, CELL))

    # стены
    for wall in walls:
        pygame.draw.rect(screen, GRAY, (*wall, CELL, CELL))

    # -------- UI --------
    score_text = font.render(f"Score: {SCORE}", True, WHITE)
    level_text = font.render(f"Level: {LEVEL}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 30))

    # -------- UPDATE --------
    pygame.display.flip()
    clock.tick(FPS)