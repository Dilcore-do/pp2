import pygame
import math
from datetime import datetime
import os

pygame.init()

WIDTH, HEIGHT = 1600, 1200
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Pro")

clock = pygame.time.Clock()

# COLORS
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

colors = [RED, GREEN, BLUE, WHITE]

current_color = BLUE
tool = "brush"
brush_size = 5

drawing = False
start_pos = None
last_pos = None

# TEXT
font = pygame.font.SysFont(None, 30)
text_input = ""
text_pos = None
typing = False

# CANVAS
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(BLACK)

# UNDO
history = []

def save_state():
    if len(history) > 20:
        history.pop(0)
    history.append(canvas.copy())

def undo():
    if history:
        canvas.blit(history.pop(), (0, 0))

# BUTTONS
buttons = []

def create_buttons():
    x = 10
    for col in colors:
        buttons.append(("color", col, pygame.Rect(x,10,50,50)))
        x += 60

    tools = ["brush","line","fill","text","rect","circle","square",
             "right_triangle","triangle","rhombus","eraser"]

    for t in tools:
        buttons.append(("tool", t, pygame.Rect(x,10,90,50)))
        x += 100

create_buttons()

def draw_toolbar():
    pygame.draw.rect(screen,(50,50,50),(0,0,WIDTH,TOOLBAR_HEIGHT))
    font_ui = pygame.font.SysFont(None,20)

    for btype,value,rect in buttons:
        if btype == "color":
            pygame.draw.rect(screen,value,rect)
        else:
            pygame.draw.rect(screen,WHITE,rect,2)
            txt = font_ui.render(value,True,WHITE)
            screen.blit(txt,(rect.x+5,rect.y+15))

def get_color():
    return BLACK if tool == "eraser" else current_color

# FLOOD FILL
def flood_fill(surface,x,y,new_color):
    target = surface.get_at((x,y))
    if target == new_color:
        return

    stack = [(x,y)]

    while stack:
        px,py = stack.pop()

        if px<0 or px>=surface.get_width() or py<0 or py>=surface.get_height():
            continue

        if surface.get_at((px,py)) != target:
            continue

        surface.set_at((px,py),new_color)

        stack += [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]

# SHAPES
def draw_right_triangle(s,c,a,b):
    pygame.draw.polygon(s,c,[a,(a[0],b[1]),b],brush_size)

def draw_equilateral_triangle(s,c,a,b):
    base = b[0]-a[0]
    h = int(abs(base)*math.sqrt(3)/2)
    pts = [a,b,((a[0]+b[0])//2,a[1]-h)]
    pygame.draw.polygon(s,c,pts,brush_size)

def draw_rhombus(s,c,a,b):
    cx = (a[0]+b[0])//2
    cy = (a[1]+b[1])//2
    dx = abs(b[0]-a[0])//2
    dy = abs(b[1]-a[1])//2
    pts = [(cx,cy-dy),(cx+dx,cy),(cx,cy+dy),(cx-dx,cy)]
    pygame.draw.polygon(s,c,pts,brush_size)

# PREVIEW
def preview(surface):
    temp = surface.copy()
    mx,my = pygame.mouse.get_pos()
    end = (mx,my-TOOLBAR_HEIGHT)

    if tool=="line":
        pygame.draw.line(temp,get_color(),start_pos,end,brush_size)

    elif tool=="rect":
        pygame.draw.rect(temp,get_color(),
            pygame.Rect(min(start_pos[0],end[0]),
                        min(start_pos[1],end[1]),
                        abs(end[0]-start_pos[0]),
                        abs(end[1]-start_pos[1])),brush_size)

    elif tool=="circle":
        r=int(math.hypot(end[0]-start_pos[0],end[1]-start_pos[1]))
        pygame.draw.circle(temp,get_color(),start_pos,r,brush_size)

    elif tool=="square":
        size=min(abs(end[0]-start_pos[0]),abs(end[1]-start_pos[1]))
        pygame.draw.rect(temp,get_color(),
            pygame.Rect(start_pos[0],start_pos[1],size,size),brush_size)

    elif tool=="right_triangle":
        draw_right_triangle(temp,get_color(),start_pos,end)

    elif tool=="triangle":
        draw_equilateral_triangle(temp,get_color(),start_pos,end)

    elif tool=="rhombus":
        draw_rhombus(temp,get_color(),start_pos,end)

    return temp

# MAIN LOOP
running=True
while running:

    screen.fill(BLACK)

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:

            # BRUSH SIZE
            if event.key==pygame.K_1: brush_size=2
            if event.key==pygame.K_2: brush_size=5
            if event.key==pygame.K_3: brush_size=10

            keys = pygame.key.get_pressed()

            # SAVE (Ctrl+S / Cmd+S on macOS)
            if event.key == pygame.K_s and (
                keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or
                keys[pygame.K_LGUI] or keys[pygame.K_RGUI]
            ):
                filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png"))
                pygame.image.save(canvas, filename)
                print("Saved:", filename)

            # UNDO (Cmd+Z)
            if event.key==pygame.K_z and mods & pygame.KMOD_META:
                undo()

            # TEXT
            if typing:
                if event.key==pygame.K_RETURN:
                    canvas.blit(font.render(text_input,True,current_color),text_pos)
                    typing=False
                elif event.key==pygame.K_ESCAPE:
                    typing=False
                elif event.key==pygame.K_BACKSPACE:
                    text_input=text_input[:-1]
                else:
                    text_input+=event.unicode

        if event.type==pygame.MOUSEBUTTONDOWN:
            x,y=event.pos

            if y<TOOLBAR_HEIGHT:
                for t,v,r in buttons:
                    if r.collidepoint(event.pos):
                        if t=="color": current_color=v
                        else: tool=v
            else:
                save_state()

                if tool=="fill":
                    flood_fill(canvas,x,y-TOOLBAR_HEIGHT,current_color)

                elif tool=="text":
                    text_pos=(x,y-TOOLBAR_HEIGHT)
                    text_input=""
                    typing=True

                else:
                    drawing=True
                    start_pos=(x,y-TOOLBAR_HEIGHT)
                    last_pos=None

        if event.type==pygame.MOUSEBUTTONUP:
            drawing=False
            last_pos=None

            if start_pos:
                end=(event.pos[0],event.pos[1]-TOOLBAR_HEIGHT)

                if tool=="line":
                    pygame.draw.line(canvas,get_color(),start_pos,end,brush_size)

                elif tool=="rect":
                    pygame.draw.rect(canvas,get_color(),
                        pygame.Rect(min(start_pos[0],end[0]),
                                    min(start_pos[1],end[1]),
                                    abs(end[0]-start_pos[0]),
                                    abs(end[1]-start_pos[1])),brush_size)

                elif tool=="circle":
                    pygame.draw.circle(canvas,get_color(),start_pos,
                        int(math.hypot(end[0]-start_pos[0],end[1]-start_pos[1])),brush_size)

                elif tool=="square":
                    size=min(abs(end[0]-start_pos[0]),abs(end[1]-start_pos[1]))
                    pygame.draw.rect(canvas,get_color(),
                        pygame.Rect(start_pos[0],start_pos[1],size,size),brush_size)

                elif tool=="right_triangle":
                    draw_right_triangle(canvas,get_color(),start_pos,end)

                elif tool=="triangle":
                    draw_equilateral_triangle(canvas,get_color(),start_pos,end)

                elif tool=="rhombus":
                    draw_rhombus(canvas,get_color(),start_pos,end)

        if event.type==pygame.MOUSEMOTION:
            if drawing and tool in ["brush","eraser"]:
                x,y=event.pos
                pos=(x,y-TOOLBAR_HEIGHT)

                if last_pos:
                    dx = pos[0] - last_pos[0]
                    dy = pos[1] - last_pos[1]
                    steps = max(abs(dx), abs(dy))

                    for i in range(steps + 1):
                        t = i / (steps + 1)
                        ix = int(last_pos[0] + dx * t)
                        iy = int(last_pos[1] + dy * t)
                        pygame.draw.circle(canvas, get_color(), (ix, iy), brush_size)

                last_pos=pos

    screen.blit(canvas,(0,TOOLBAR_HEIGHT))

    if drawing and start_pos and tool not in ["brush","eraser","fill","text"]:
        screen.blit(preview(canvas),(0,TOOLBAR_HEIGHT))

    if typing and text_pos:
        screen.blit(font.render(text_input,True,current_color),
                    (text_pos[0],text_pos[1]+TOOLBAR_HEIGHT))

    draw_toolbar()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()