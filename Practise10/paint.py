import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")

clock = pygame.time.Clock()

# цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

colors = [RED, GREEN, BLUE, WHITE]

current_color = BLUE
tool = "brush"
radius = 8

drawing = False
last_pos = None
start_pos = None

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(BLACK)

buttons = []

def create_buttons():
    x = 10
    
    # цвета
    for col in colors:
        rect = pygame.Rect(x, 10, 50, 50)
        buttons.append(("color", col, rect))
        x += 60

    # инструменты
    tools = ["brush", "rect", "circle", "eraser"]
    for t in tools:
        rect = pygame.Rect(x, 10, 80, 50)
        buttons.append(("tool", t, rect))
        x += 90

create_buttons()

def draw_toolbar():
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    
    font = pygame.font.SysFont(None, 24)
    
    for btype, value, rect in buttons:
        if btype == "color":
            pygame.draw.rect(screen, value, rect)
        else:
            pygame.draw.rect(screen, WHITE, rect, 2)
            text = font.render(value, True, WHITE)
            screen.blit(text, (rect.x + 5, rect.y + 15))

def get_color():
    return BLACK if tool == "eraser" else current_color

# 🔥 плавная линия (решает проблему прерывистости)
def draw_smooth_line(surface, color, start, end, radius):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    for i in range(steps):
        t = i / steps
        x = int(start[0] + dx * t)
        y = int(start[1] + dy * t)
        pygame.draw.circle(surface, color, (x, y), radius)

running = True

while running:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if y < TOOLBAR_HEIGHT:
                for btype, value, rect in buttons:
                    if rect.collidepoint(event.pos):
                        if btype == "color":
                            current_color = value
                        else:
                            tool = value
            else:
                drawing = True
                start_pos = (x, y - TOOLBAR_HEIGHT)
                last_pos = start_pos
        
        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                end_pos = (event.pos[0], event.pos[1] - TOOLBAR_HEIGHT)
                
                if tool == "rect":
                    rect = pygame.Rect(start_pos, (
                        end_pos[0] - start_pos[0],
                        end_pos[1] - start_pos[1]
                    ))
                    pygame.draw.rect(canvas, get_color(), rect, 2)
                
                elif tool == "circle":
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    r = int((dx**2 + dy**2) ** 0.5)
                    pygame.draw.circle(canvas, get_color(), start_pos, r, 2)
            
            drawing = False
            last_pos = None
        
        if event.type == pygame.MOUSEMOTION:
            if drawing and tool in ["brush", "eraser"]:
                x, y = event.pos
                pos = (x, y - TOOLBAR_HEIGHT)

                if last_pos is not None:
                    draw_smooth_line(canvas, get_color(), last_pos, pos, radius)

                last_pos = pos

    screen.fill(BLACK)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    draw_toolbar()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()