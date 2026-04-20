# ===================== IMPORTS =====================
import pygame, sys
from pygame.locals import *
import random, time

# ===================== INIT =====================
pygame.init()

# FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# ===================== COLORS =====================
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ===================== GAME SETTINGS =====================
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

SPEED = 5
SCORE = 0
COINS = 0

# ускорение врага
COIN_THRESHOLD = 5
SPEED_STEP = 1

# ===================== FONTS =====================
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# ===================== LOAD IMAGES =====================
background = pygame.image.load("media/AnimatedStreet.png")

# ===================== DISPLAY =====================
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

# ===================== GROUPS =====================
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# ===================== ENEMY CLASS =====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("media/Enemy.png")
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # случайная позиция сверху
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE

        self.rect.move_ip(0, SPEED)

        # если вышел за экран
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()

# ===================== PLAYER CLASS =====================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("media/Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# ===================== COIN CLASS =====================
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # вес монеты
        self.value = random.choice([1, 2, 3])

        # картинки
        if self.value == 1:
            self.image = pygame.image.load("media/coin.png")
        elif self.value == 2:
            self.image = pygame.image.load("media/coin2.png")
        else:
            self.image = pygame.image.load("media/coin3.png")

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # безопасный спавн (НЕ на враге)
        safe = False

        while not safe:
            x = random.randint(40, SCREEN_WIDTH - 40)
            y = random.randint(-150, -20)

            self.rect.center = (x, y)

            safe = True
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    safe = False
                    break

    def move(self):
        self.rect.move_ip(0, SPEED)

        # если ушла вниз → новая позиция
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()

# ===================== CREATE OBJECTS =====================
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies.add(E1)
coins.add(C1)

all_sprites.add(P1, E1, C1)

# ===================== SPEED EVENT =====================
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# ===================== GAME LOOP =====================
while True:

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.2

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # -------- BACKGROUND --------
    DISPLAYSURF.blit(background, (0, 0))

    # -------- UI --------
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Coins: " + str(COINS), True, BLACK)

    DISPLAYSURF.blit(score_text, (10, 10))
    DISPLAYSURF.blit(coin_text, (250, 10))

    # -------- MOVE OBJECTS --------
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # -------- COIN COLLISION --------
    collected = pygame.sprite.spritecollide(P1, coins, True)

    for coin in collected:
        # добавляем очки
        COINS += coin.value

        # ускорение врага каждые N монет
        if COINS % COIN_THRESHOLD == 0:
            SPEED += SPEED_STEP

        # новая монета
        new_coin = Coin()
        coins.add(new_coin)
        all_sprites.add(new_coin)

    # -------- ENEMY COLLISION --------
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('media/crash.wav').play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))

        pygame.display.update()
        time.sleep(2)

        pygame.quit()
        sys.exit()

    # -------- UPDATE SCREEN --------
    pygame.display.update()
    FramePerSec.tick(FPS)