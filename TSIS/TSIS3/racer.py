import pygame, sys, random, time, json, os
from pygame.locals import *

pygame.init()

# ================= FILES =================
SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

def load_json(file, default):
    if not os.path.exists(file):
        return default
    return json.load(open(file))

def save_json(file, data):
    json.dump(data, open(file, "w"), indent=4)

settings = load_json(SETTINGS_FILE, {"sound": True, "difficulty": "normal", "car_color": "blue"})
leaderboard = load_json(LEADERBOARD_FILE, [])

# ================= BASIC =================
FPS = 60
clock = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

font = pygame.font.SysFont("Verdana", 40)
small = pygame.font.SysFont("Verdana", 20)

background = pygame.image.load("media/AnimatedStreet.png")

# ================= CLASSES =================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        color = settings.get("car_color", "blue")
        self.image = pygame.image.load(f"media/Player_{color}.png")
        self.rect = self.image.get_rect(center=(200,520))
        self.shield = False

    def move(self):
        keys = pygame.key.get_pressed()
        if self.rect.left > 0 and keys[K_LEFT]:
            self.rect.move_ip(-5,0)
        if self.rect.right < SCREEN_WIDTH and keys[K_RIGHT]:
            self.rect.move_ip(5,0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("media/Enemy.png")
        self.rect = self.image.get_rect(center=(random.randint(40,360),0))

    def move(self, speed):
        self.rect.move_ip(0,speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.center = (random.randint(40,360),0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.value = random.choice([1,2,3])

        if self.value == 1:
            self.image = pygame.image.load("media/coin.png")
        elif self.value == 2:
            self.image = pygame.image.load("media/coin2.png")
        else:
            self.image = pygame.image.load("media/coin3.png")

        self.rect = self.image.get_rect(center=(random.randint(40,360),-50))

    def move(self, speed):
        self.rect.move_ip(0,speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("media/obstacle.png")
        self.rect = self.image.get_rect(center=(random.randint(40,360),-50))

    def move(self, speed):
        self.rect.move_ip(0,speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["nitro","shield","repair"])

        if self.type == "nitro":
            self.image = pygame.image.load("media/nitro.png")
        elif self.type == "shield":
            self.image = pygame.image.load("media/shield.png")
        else:
            self.image = pygame.image.load("media/repair.png")

        self.rect = self.image.get_rect(center=(random.randint(40,360),-50))
        self.spawn_time = time.time()

    def move(self, speed):
        self.rect.move_ip(0,speed)
        if time.time() - self.spawn_time > 5:
            self.kill()

# ================= GAME =================
def game(username):
    SPEED = 5

    # difficulty scaling
    if settings.get("difficulty", "normal") == "easy":
        SPEED = 4
    elif settings.get("difficulty", "normal") == "hard":
        SPEED = 7
    SCORE = 0
    COINS = 0
    DIST = 0
    HP = 2
    MAX_HP = 2
    last_hit_time = 0
    INVULN_TIME = 1.0

    ACTIVE = None
    POWER_TIME = 0

    P1 = Player()

    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)

    spawn_timer = 0

    while True:
        DISPLAYSURF.blit(background,(0,0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

        spawn_timer += 1

        enemy_rate = 90
        obstacle_rate = 120

        if settings.get("difficulty", "normal") == "easy":
            enemy_rate = 120
            obstacle_rate = 160
        elif settings.get("difficulty", "normal") == "hard":
            enemy_rate = 60
            obstacle_rate = 90

        if spawn_timer % enemy_rate == 0 and len(enemies) < 3:
            enemies.add(Enemy())

        if spawn_timer % 80 == 0:
            coins.add(Coin())

        if spawn_timer % obstacle_rate == 0:
            obstacles.add(Obstacle())

        if random.randint(1, 700) == 1:
            powerups.add(PowerUp())

        # draw & move
        for g in [enemies, coins, obstacles, powerups]:
            for obj in g:
                obj.move(SPEED)
                DISPLAYSURF.blit(obj.image, obj.rect)

        P1.move()
        DISPLAYSURF.blit(P1.image, P1.rect)

        DIST += 1

        # collisions
        if pygame.sprite.spritecollideany(P1, enemies) or pygame.sprite.spritecollideany(P1, obstacles):

            # invincibility frames
            if time.time() - last_hit_time < INVULN_TIME:
                pass
            else:
                last_hit_time = time.time()

                if P1.shield:
                    P1.shield = False
                else:
                    HP -= 1

                    if settings["sound"]:
                        pygame.mixer.Sound("media/crash.wav").play()

                    if HP <= 0:
                        return SCORE, DIST, COINS

        for c in pygame.sprite.spritecollide(P1, coins, True):
            COINS += c.value
            SCORE += c.value

        for p in pygame.sprite.spritecollide(P1, powerups, True):

            if p.type == "shield":
                P1.shield = True

            elif p.type == "repair":
                HP = min(MAX_HP, HP + 1)

            elif p.type == "nitro":
                ACTIVE = "nitro"
                POWER_TIME = time.time()

        # nitro
        if ACTIVE == "nitro":
            if time.time() - POWER_TIME < 4:
                SPEED = 10
            else:
                SPEED = 5
                ACTIVE = None

        # UI
        DISPLAYSURF.blit(small.render(f"Score:{SCORE}",True,(0,0,0)),(10,10))
        DISPLAYSURF.blit(small.render(f"Coins:{COINS}",True,(0,0,0)),(10,30))
        DISPLAYSURF.blit(small.render(f"Dist:{int(DIST)}",True,(0,0,0)),(10,50))
        DISPLAYSURF.blit(small.render(f"HP:{HP}",True,(0,0,0)),(10,70))

        pygame.display.update()
        clock.tick(FPS)

# ================= MENU =================
def menu():
    username = ""
    active_input = False
    while True:
        DISPLAYSURF.fill((255,255,255))

        DISPLAYSURF.blit(font.render("RACER",True,(0,0,0)),(120,100))

        # input box
        pygame.draw.rect(DISPLAYSURF, (0,0,0), (100, 200, 200, 30), 2)
        name_text = small.render("Name: " + username, True, (0,0,0))
        DISPLAYSURF.blit(name_text, (110, 205))

        buttons = ["Play","Leaderboard","Settings","Quit"]

        for i,b in enumerate(buttons):
            DISPLAYSURF.blit(small.render(b,True,(0,0,0)),(150,250+i*40))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()

                # activate input box
                if 200 < y < 230:
                    active_input = True
                else:
                    active_input = False

                if 250<y<280:
                    if username.strip() == "":
                        username = "Player"

                    score,dist,coins = game(username)

                    leaderboard.append({"name":username,"score":score,"dist":int(dist)})
                    leaderboard.sort(key=lambda x:x["score"],reverse=True)
                    save_json(LEADERBOARD_FILE,leaderboard[:10])

                if 290<y<320:
                    show_leaderboard()

                if 330<y<360:
                    settings_screen()

                if 370<y<400:
                    pygame.quit(); sys.exit()

            if event.type == KEYDOWN and active_input:
                if event.key == K_BACKSPACE:
                    username = username[:-1]
                elif event.key == K_RETURN:
                    pass
                else:
                    if len(username) < 12:
                        username += event.unicode

        pygame.display.update()

# ================= LEADERBOARD =================
def show_leaderboard():
    while True:
        DISPLAYSURF.fill((255,255,255))

        for i,e in enumerate(leaderboard[:10]):
            DISPLAYSURF.blit(small.render(f"{i+1}. {e['name']} {e['score']}",True,(0,0,0)),(50,100+i*30))

        DISPLAYSURF.blit(small.render("Back",True,(0,0,0)),(170,500))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return

        pygame.display.update()

# ================= SETTINGS =================
def settings_screen():
    while True:
        DISPLAYSURF.fill((255,255,255))

        # TITLE SECTIONS
        DISPLAYSURF.blit(small.render("Settings", True, (0,0,0)), (150, 40))

        # ================= CAR COLOR =================
        DISPLAYSURF.blit(small.render("Car Color:", True, (0,0,0)), (100, 80))

        pygame.draw.rect(DISPLAYSURF,(0,0,255),(100,110,40,40))  # blue
        pygame.draw.rect(DISPLAYSURF,(255,0,0),(160,110,40,40))  # red
        pygame.draw.rect(DISPLAYSURF,(0,255,0),(220,110,40,40))  # green

        # ================= DIFFICULTY =================
        DISPLAYSURF.blit(small.render("Difficulty:", True, (0,0,0)), (100, 170))

        pygame.draw.rect(DISPLAYSURF,(200,200,200),(100,200,40,40))  # easy
        pygame.draw.rect(DISPLAYSURF,(150,150,150),(160,200,40,40))  # normal
        pygame.draw.rect(DISPLAYSURF,(100,100,100),(220,200,40,40))  # hard

        # ================= SOUND =================
        DISPLAYSURF.blit(small.render(f"Sound: {settings['sound']}", True, (0,0,0)), (100, 270))
        pygame.draw.rect(DISPLAYSURF,(180,180,180),(100,300,160,40))
        DISPLAYSURF.blit(small.render("Toggle Sound", True, (0,0,0)), (110, 310))

        # ================= BACK =================
        pygame.draw.rect(DISPLAYSURF,(0,0,0),(150,500,100,40))
        DISPLAYSURF.blit(small.render("Back", True, (255,255,255)), (175, 510))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()

                # car color selection
                if 110 <= y <= 150:
                    if 100 <= x <= 140:
                        settings["car_color"] = "blue"
                    elif 160 <= x <= 200:
                        settings["car_color"] = "red"
                    elif 220 <= x <= 260:
                        settings["car_color"] = "green"
                    save_json(SETTINGS_FILE, settings)

                # difficulty selection
                if 200 <= y <= 240:
                    if 100 <= x <= 140:
                        settings["difficulty"] = "easy"
                    elif 160 <= x <= 200:
                        settings["difficulty"] = "normal"
                    elif 220 <= x <= 260:
                        settings["difficulty"] = "hard"
                    save_json(SETTINGS_FILE, settings)

                # sound toggle
                if 300 <= y <= 340 and 100 <= x <= 260:
                    settings["sound"] = not settings["sound"]
                    save_json(SETTINGS_FILE, settings)

                # back button
                if 500 <= y <= 540 and 150 <= x <= 250:
                    return

        pygame.display.update()

# ================= START =================
menu()