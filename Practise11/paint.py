import pygame
import math

pygame.init()

# ===================== WINDOW =====================
WIDTH, HEIGHT = 1200, 900
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")

clock = pygame.time.Clock()

# ===================== COLORS =====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

colors = [RED, GREEN, BLUE, WHITE]

current_color = BLUE
tool = "brush"

radius = 6

drawing = False
start_pos = None
last_pos = None

# ===================== CANVAS =====================
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(BLACK)

buttons = []

# ===================== BUTTONS =====================
def create_buttons():
    x = 10

    # colors
    for col in colors:
        rect = pygame.Rect(x, 10, 50, 50)
        buttons.append(("color", col, rect))
        x += 60

    # tools
    tools = ["brush", "square", "rect", "circle", "right_triangle", "triangle", "rhombus", "eraser"]

    for t in tools:
        rect = pygame.Rect(x, 10, 90, 50)
        buttons.append(("tool", t, rect))
        x += 100

create_buttons()

# ===================== UI =====================
def draw_toolbar():
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, WIDTH, TOOLBAR_HEIGHT))

    font = pygame.font.SysFont(None, 20)

    for btype, value, rect in buttons:
        if btype == "color":
            pygame.draw.rect(screen, value, rect)
        else:
            pygame.draw.rect(screen, WHITE, rect, 2)
            text = font.render(value, True, WHITE)
            screen.blit(text, (rect.x + 5, rect.y + 15))

def get_color():
    return BLACK if tool == "eraser" else current_color

# ===================== SHAPES =====================
def draw_right_triangle(surface, color, start, end):
    points = [start, (start[0], end[1]), end]
    pygame.draw.polygon(surface, color, points, 2)

def draw_equilateral_triangle(surface, color, start, end):
    base = end[0] - start[0]
    height = int(math.sqrt(3) / 2 * abs(base))

    points = [
        start,
        end,
        ((start[0] + end[0]) // 2, start[1] - height)
    ]

    pygame.draw.polygon(surface, color, points, 2)

def draw_rhombus(surface, color, start, end):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2

    dx = abs(end[0] - start[0]) // 2
    dy = abs(end[1] - start[1]) // 2

    points = [
        (cx, cy - dy),
        (cx + dx, cy),
        (cx, cy + dy),
        (cx - dx, cy)
    ]

    pygame.draw.polygon(surface, color, points, 2)

# ===================== PREVIEW =====================
def draw_preview(surface, tool, color, start, end):
    temp = surface.copy()

    x1, y1 = start
    x2, y2 = end

    if tool == "rect":
        rect = pygame.Rect(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1)
        )
        pygame.draw.rect(temp, color, rect, 2)

    elif tool == "square":
        size = min(abs(x2 - x1), abs(y2 - y1))
        rect = pygame.Rect(
            x1 if x2 > x1 else x1 - size,
            y1 if y2 > y1 else y1 - size,
            size,
            size
        )
        pygame.draw.rect(temp, color, rect, 2)

    elif tool == "circle":
        r = int(math.hypot(x2 - x1, y2 - y1))
        pygame.draw.circle(temp, color, start, r, 2)

    elif tool == "right_triangle":
        draw_right_triangle(temp, color, start, end)

    elif tool == "triangle":
        draw_equilateral_triangle(temp, color, start, end)

    elif tool == "rhombus":
        draw_rhombus(temp, color, start, end)

    return temp

# ===================== MAIN LOOP =====================
running = True

while running:

    screen.fill(BLACK)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ===================== CLICK =====================
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
                last_pos = None

        # ===================== RELEASE =====================
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            last_pos = None

            if start_pos:
                end_pos = (event.pos[0], event.pos[1] - TOOLBAR_HEIGHT)

                color = get_color()
                x1, y1 = start_pos
                x2, y2 = end_pos

                if tool == "rect":
                    rect = pygame.Rect(
                        min(x1, x2),
                        min(y1, y2),
                        abs(x2 - x1),
                        abs(y2 - y1)
                    )
                    pygame.draw.rect(canvas, color, rect, 2)

                elif tool == "square":
                    size = min(abs(x2 - x1), abs(y2 - y1))
                    rect = pygame.Rect(
                        x1 if x2 > x1 else x1 - size,
                        y1 if y2 > y1 else y1 - size,
                        size,
                        size
                    )
                    pygame.draw.rect(canvas, color, rect, 2)

                elif tool == "circle":
                    r = int(math.hypot(x2 - x1, y2 - y1))
                    pygame.draw.circle(canvas, color, start_pos, r, 2)

                elif tool == "right_triangle":
                    draw_right_triangle(canvas, color, start_pos, end_pos)

                elif tool == "triangle":
                    draw_equilateral_triangle(canvas, color, start_pos, end_pos)

                elif tool == "rhombus":
                    draw_rhombus(canvas, color, start_pos, end_pos)

        # ===================== SMOOTH BRUSH (FIXED) =====================
        if event.type == pygame.MOUSEMOTION:
            if drawing and tool in ["brush", "eraser"]:

                x, y = event.pos
                pos = (x, y - TOOLBAR_HEIGHT)

                if last_pos is not None:
                    dx = pos[0] - last_pos[0]
                    dy = pos[1] - last_pos[1]
                    steps = max(abs(dx), abs(dy))

                    for i in range(steps + 1):
                        t = i / (steps + 1)
                        ix = int(last_pos[0] + dx * t)
                        iy = int(last_pos[1] + dy * t)

                        pygame.draw.circle(canvas, get_color(), (ix, iy), radius)

                pygame.draw.circle(canvas, get_color(), pos, radius)

                last_pos = pos

    # ===================== DRAW =====================
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # ===================== PREVIEW =====================
    if drawing and start_pos and tool not in ["brush", "eraser"]:
        mouse_pos = pygame.mouse.get_pos()
        end = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

        preview = draw_preview(canvas, tool, get_color(), start_pos, end)
        screen.blit(preview, (0, TOOLBAR_HEIGHT))

    draw_toolbar()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()