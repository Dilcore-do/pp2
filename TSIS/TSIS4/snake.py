# ===================== IMPORTS =====================
import pygame
import random
import sys
import time
import psycopg2
import json
import os

# ===================== DB =====================
conn = psycopg2.connect(
    dbname="snake",
    user="postgres",
    password="FadeQewzi2007!",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def get_or_create_user(username):
    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    user = cur.fetchone()
    if user:
        return user[0]

    cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
    conn.commit()
    return cur.fetchone()[0]

def save_score(username, score, level):
    user_id = get_or_create_user(username)

    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s,%s,%s)",
        (user_id, score, level)
    )
    conn.commit()

def get_top10():
    cur.execute("""
        SELECT username, score, level_reached, played_at
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY score DESC
        LIMIT 10
    """)
    return cur.fetchall()

def get_best_score(username):
    cur.execute("""
        SELECT MAX(score)
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        WHERE username=%s
    """, (username,))
    res = cur.fetchone()[0]
    return res if res else 0

# ===================== INIT =====================
pygame.init()
pygame.mixer.init()

WIDTH = 600
HEIGHT = 400
CELL = 20

FPS = 10
base_FPS = FPS
LEVEL = 1
SCORE = 0

FOOD_LIFETIME = 5
food_spawn_time = 0

WHITE = (255,255,255)
GREEN = (0,200,0)
RED = (200,0,0)
GRAY = (100,100,100)
BLACK = (0,0,0)

SETTINGS_FILE='settings.json'
DEFAULT_SETTINGS={'snake_color':[0,200,0],'grid':False,'sound':True}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_FILE = os.path.join(BASE_DIR, 'assets', 'track1.mp3')
if not os.path.exists(MUSIC_FILE):
    alt_music = os.path.join(BASE_DIR, 'assets', 'track1.wav')
    if os.path.exists(alt_music):
        MUSIC_FILE = alt_music

def apply_music_setting():
    try:
        if settings['sound']:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
    except:
        pass

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE,'r',encoding='utf-8') as f:
                data=json.load(f)
                for k,v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        data[k]=v
                return data
        except:
            pass
    with open(SETTINGS_FILE,'w',encoding='utf-8') as f:
        json.dump(DEFAULT_SETTINGS,f,indent=2)
    return DEFAULT_SETTINGS.copy()

settings=load_settings()
# music starts based on saved settings after settings loaded
GREEN=tuple(settings['snake_color'])
apply_music_setting()

def save_settings():
    with open(SETTINGS_FILE,'w',encoding='utf-8') as f:
        json.dump(settings,f,indent=2)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake PRO")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 40)

# ===================== USERNAME SCREEN =====================
def username_screen():
    username = ""
    while True:
        screen.fill(BLACK)

        title = big_font.render("Enter Username", True, WHITE)
        text = font.render(username, True, GREEN)

        screen.blit(title, (150, 120))
        screen.blit(text, (200, 200))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and username:
                    return username
                elif e.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += e.unicode

# ===================== LEADERBOARD SCREEN =====================
def leaderboard_screen():
    data = get_top10()

    while True:
        screen.fill(BLACK)

        title = big_font.render("TOP 10", True, WHITE)
        screen.blit(title, (220, 20))

        y = 80
        for i, row in enumerate(data):
            text = f"{i+1}. {row[0]}  {row[1]}  lvl:{row[2]}"
            screen.blit(font.render(text, True, WHITE), (100, y))
            y += 30

        screen.blit(font.render("ESC - back", True, GRAY), (220, 350))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

def settings_screen():
    global GREEN
    palette=[(0,200,0),(255,255,0),(0,255,255),(255,0,255),(255,128,0)]
    while True:
        screen.fill(BLACK)
        lines=[
        '1 Toggle Grid: '+('ON' if settings['grid'] else 'OFF'),
        '2 Toggle Sound: '+('ON' if settings['sound'] else 'OFF'),
        '3 Change Snake Color',
        'S Save and Back']
        screen.blit(big_font.render('SETTINGS',True,WHITE),(170,50))
        y=130
        for t in lines:
            screen.blit(font.render(t,True,WHITE),(120,y)); y+=50
        pygame.draw.rect(screen,GREEN,(400,230,40,40))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_1: settings['grid']=not settings['grid']
                if e.key==pygame.K_2:
                    settings['sound']=not settings['sound']
                    apply_music_setting()
                if e.key==pygame.K_3:
                    i=(palette.index(tuple(settings['snake_color']))+1)%len(palette) if tuple(settings['snake_color']) in palette else 0
                    settings['snake_color']=list(palette[i]); GREEN=tuple(settings['snake_color'])
                if e.key==pygame.K_s or e.key==pygame.K_ESCAPE:
                    save_settings()
                    apply_music_setting()
                    return

def main_menu():
    options=['Play','Leaderboard','Settings','Exit']
    selected=0
    while True:
        screen.fill(BLACK)
        screen.blit(big_font.render('SNAKE PRO',True,WHITE),(170,60))
        y=150
        for i,opt in enumerate(options):
            prefix='> ' if i==selected else '  '
            screen.blit(font.render(prefix+opt,True,WHITE),(220,y)); y+=50
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP: selected=(selected-1)%4
                if e.key==pygame.K_DOWN: selected=(selected+1)%4
                if e.key==pygame.K_RETURN:
                    if selected==0: return
                    if selected==1: leaderboard_screen()
                    if selected==2: settings_screen()
                    if selected==3: pygame.quit(); sys.exit()

def game_over_menu():
    global snake,direction,SCORE,LEVEL,base_FPS,food,poison,food_spawn_time,poison_spawn_time,walls
    while True:
        screen.fill(BLACK)
        msgs=['GAME OVER',f'Score: {SCORE}',f'Level: {LEVEL}',f'Best: {personal_best}','R - Replay','M - Main Menu']
        y=90
        for i,m in enumerate(msgs):
            f=big_font if i==0 else font
            screen.blit(f.render(m,True,WHITE),(170 if i==0 else 180,y)); y+=50
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r:
                    snake=[(100,100),(80,100),(60,100)]
                    direction=(CELL,0)
                    SCORE=0; LEVEL=1; base_FPS=10
                    generate_walls(LEVEL)
                    food=generate_food(); poison=generate_food()
                    food_spawn_time=time.time(); poison_spawn_time=time.time()
                    return
                if e.key==pygame.K_m:
                    main_menu()
                    snake=[(100,100),(80,100),(60,100)]
                    direction=(CELL,0)
                    SCORE=0; LEVEL=1; base_FPS=10
                    generate_walls(LEVEL)
                    food=generate_food(); poison=generate_food()
                    return

# ===================== USER =====================
username = username_screen()
main_menu()
personal_best = get_best_score(username)

# ===================== SNAKE =====================
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL, 0)

# ===================== WALLS (ИЗМЕНЕНО) =====================
walls = []

def generate_walls(level):
    walls.clear()

    # Внешние границы
    for x in range(0, WIDTH, CELL):
        walls.append((x, 0))
        walls.append((x, HEIGHT - CELL))

    for y in range(0, HEIGHT, CELL):
        walls.append((0, y))
        walls.append((WIDTH - CELL, y))

    # Случайные препятствия только с 3-го уровня
    if level >= 3:
        num_obstacles = (level - 2) * 7
        count = 0
        while count < num_obstacles:
            rx = random.randrange(CELL, WIDTH - CELL, CELL)
            ry = random.randrange(CELL, HEIGHT - CELL, CELL)
            
            # Проверка, чтобы не заблокировать змею (минимум 3 клетки от головы)
            head_x, head_y = snake[0]
            if (
                (rx, ry) not in snake
                and abs(rx - head_x) > CELL * 3
                and abs(ry - head_y) > CELL * 3
            ):
                if (rx, ry) not in walls:
                    walls.append((rx, ry))
                    count += 1

generate_walls(LEVEL)

# ===================== FOOD =====================
def generate_food():
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)

        if (x, y) not in snake and (x, y) not in walls:
            return (x, y)

food = generate_food()
food_value = random.choice([1, 2, 3])
food_spawn_time = time.time()
poison = generate_food()
poison_spawn_time = time.time()

# ===================== POWERUPS =====================
powerup = None
power_type = None
power_spawn_time = pygame.time.get_ticks()
effect_end_time = 0
active_speed = "normal"
shield_ready = False
paused = False

POWERUP_COLORS = {
    "speed": (0, 255, 0),
    "slow": (75, 0, 130),
    "shield": (0, 0, 255)
}

# ===================== GAME OVER =====================
def game_over():
    save_score(username, SCORE, LEVEL)
    game_over_menu()

# ===================== GAME LOOP =====================
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL):
                direction = (0, -CELL)
            if event.key == pygame.K_DOWN and direction != (0, -CELL):
                direction = (0, CELL)
            if event.key == pygame.K_LEFT and direction != (CELL, 0):
                direction = (-CELL, 0)
            if event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                direction = (CELL, 0)

            if event.key == pygame.K_l:
                leaderboard_screen()

            if paused:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    paused = False

    if paused:
        msg = big_font.render("MOVE TO CONTINUE", True, WHITE)
        screen.blit(msg, (120, 180))
        pygame.display.flip()
        clock.tick(10)
        continue

    head_x = snake[0][0] + direction[0]
    head_y = snake[0][1] + direction[1]
    new_head = (head_x, head_y)

    # -------- COLLISIONS --------
    if new_head in walls or head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT or new_head in snake:
        if shield_ready:
            shield_ready = False
            snake.append(snake[-1])
            paused = True
        else:
            game_over()
    else:
        snake.insert(0, new_head)

    # -------- FOOD EAT (ИЗМЕНЕНО: +5 SCORE) --------
    if new_head == food:
        old_score = SCORE
        SCORE += food_value
        if SCORE > personal_best:
            personal_best = SCORE

        # Переход на новый уровень за каждые 5 очков
        if (SCORE // 5) > (old_score // 5):
            LEVEL += 1
            base_FPS += 2
            generate_walls(LEVEL)
            # Пересоздаем яд и еду, чтобы они не попали в новые стены
            food = generate_food()
            poison = generate_food()

        food = generate_food()
        food_value = random.choice([1, 2, 3])
        food_spawn_time = time.time()
    else:
        snake.pop()

    # -------- POISON --------
    if new_head == poison:
        snake = snake[:-2]
        if len(snake) <= 1:
            game_over()
        poison = generate_food()
        poison_spawn_time = time.time()

    if time.time() - poison_spawn_time > 6:
        poison = generate_food()
        poison_spawn_time = time.time()

    if time.time() - food_spawn_time > FOOD_LIFETIME:
        food = generate_food()
        food_value = random.choice([1, 2, 3])
        food_spawn_time = time.time()

    # -------- POWERUP --------
    if powerup and new_head == powerup:
        if power_type == "speed":
            active_speed = "speed"
            effect_end_time = pygame.time.get_ticks() + 5000
        elif power_type == "slow":
            active_speed = "slow"
            effect_end_time = pygame.time.get_ticks() + 5000
        elif power_type == "shield":
            shield_ready = True
        powerup = None
        power_spawn_time = pygame.time.get_ticks()

    if powerup is None and pygame.time.get_ticks() - power_spawn_time > 3000:
        powerup = generate_food()
        power_type = random.choice(["speed", "slow", "shield"])
        power_spawn_time = pygame.time.get_ticks()

    if powerup and pygame.time.get_ticks() - power_spawn_time > 8000:
        powerup = None

    if effect_end_time != 0 and pygame.time.get_ticks() >= effect_end_time:
        effect_end_time = 0
        active_speed = "normal"

    # -------- DRAW --------
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL, CELL))

    f_color = RED if food_value == 1 else (255, 165, 0) if food_value == 2 else (255, 255, 0)
    pygame.draw.rect(screen, f_color, (*food, CELL, CELL))
    pygame.draw.rect(screen, (139, 0, 0), (*poison, CELL, CELL))

    if powerup:
        pygame.draw.rect(screen, POWERUP_COLORS.get(power_type), (*powerup, CELL, CELL))

    for wall in walls:
        pygame.draw.rect(screen, GRAY, (*wall, CELL, CELL))

    # UI
    screen.blit(font.render(f"Score: {SCORE}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {LEVEL}", True, WHITE), (10, 30))
    screen.blit(font.render(f"Best: {personal_best}", True, WHITE), (10, 50))

    if settings['grid']:
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen,(40,40,40),(x,0),(x,HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen,(40,40,40),(0,y),(WIDTH,y))

    pygame.display.flip()

    if active_speed == "normal":
        FPS = base_FPS
    elif active_speed == "speed":
        FPS = int(base_FPS * 1.5)
    elif active_speed == "slow":
        FPS = max(3, int(base_FPS * 0.6))
    clock.tick(FPS)