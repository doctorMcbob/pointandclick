import pygame
from pygame import Surface, Rect
from pygame.locals import *

from src.utils import expect_click, expect_input, select_from_list, load_spritesheet, get_text_input

from src.spritesheets import ROOM_SPRITESHEET, UX_SPRITESHEET, ACTOR_SPRITESHEET, ITEM_SPRITESHEET, MOUSE_SPRITESHEET
from src.rooms import ROOMS
from src.actors import ACTORS
from src.items import ITEMS

SAVED = False
TITLE = "Point and Click Editor"
IMG_LOCATION = "src/img/"

SHEETS = {
    "rooms.png"  : ROOM_SPRITESHEET,
    "menu.png"  : UX_SPRITESHEET,
    "actor.png" : ACTOR_SPRITESHEET,
    "items.png"  : ITEM_SPRITESHEET,
    "mouse.png" : MOUSE_SPRITESHEET,
}

IMAGES = {}

def draw(G):
    G["SCREEN"].fill((1, 255, 1))
    room = ROOMS[G["ROOM"]]
    G["SCREEN"].blit(G["ROOMIMG"][room["IMG"]], (0, 0))

    for name in ACTORS:
        actor = ACTORS[name]
        pos, dim = actor["RECT"]
        G["SCREEN"].blit(G["ACTORIMG"][actor["IMG"]], pos)
        
    for name in ITEMS:
        item = ITEMS[name]
        pos, dim = item["RECT"]
        G["SCREEN"].blit(G["ITEMIMG"][item["IMG"]], pos)

def load_images(G):
    G.update({
        "ROOMIMG": load_spritesheet("rooms.png", ROOM_SPRITESHEET),
        "SYSIMG": load_spritesheet("menu.png",  UX_SPRITESHEET),
        "ACTORIMG": load_spritesheet("actor.png",  ACTOR_SPRITESHEET),
        "MOUSEIMG": load_spritesheet("mouse.png", MOUSE_SPRITESHEET),
        "ITEMIMG" : load_spritesheet("items.png", MOUSE_SPRITESHEET),
    })
    for filename in SHEETS.keys():
        IMAGES[filename] = pygame.image.load(IMG_LOCATION+filename).convert()

def setup_editor(STARTING_ROOM="ROOT"):
    G = {
        "SCREEN": pygame.display.set_mode((1080+256, 840)),
        "HEL16": pygame.font.SysFont("Helvetica", 16),
        "HEL32": pygame.font.SysFont("Helvetica", 32),

        "ROOM": STARTING_ROOM,
    }
    pygame.display.set_caption(TITLE)

    return G

def run_editor(G):
    load_images(G)
    while True:
        draw(G)
        inp = expect_input()
        mods = pygame.key.get_mods()
        
        if inp == K_ESCAPE and (SAVED or mods & KMOD_CTRL):
            return

        if inp == K_s and mods & KMOD_CTRL:
            save()

        if inp == K_s and mods & KMOD_SHIFT:
            name = select_from_list(G, list(SHEETS.keys()), (0, 0))
            spritesheet_editor(G, name)

        if inp == K_l and mods & KMOD_SHIFT:
            load_images(G)

def drawn_spritesheet_data(G, d, idx=None):
    keys = d.keys()
    surf = Surface((512, (len(d.keys()) + 1) * 16))
    surf.fill((255, 255, 255))
    for i, key in enumerate(keys):
        col = (200, 0, 120) if i == idx else (0, 0, 0)
        surf.blit(G["HEL16"].render(key, 0 , col), (0, i * 16))
        surf.blit(G["HEL16"].render(str(d[key]), 0 , col), (128, i * 16))
    if idx is not None:
        col = (200, 0, 120) if idx == len(d) else (0, 0, 0)
        surf.blit(G["HEL16"].render("ADD...", 0 , col), (0, (len(keys)) * 16))
    return surf

def make_rect(pos, pos2):
    x1 = min(pos[0], pos2[0])
    x2 = max(pos[0], pos2[0])
    y1 = min(pos[1], pos2[1])
    y2 = max(pos[1], pos2[1])
    return (x1, y1), ((x2 - x1), (y2 - y1))

def spritesheet_editor(G, name):
    sheet = SHEETS[name]
    SX, SY = (0, 0)
    CX, CY = (0, 0)
    corner = None
    
    idx = 0
    keys = list(sheet.keys())

    while True:
        G["SCREEN"].fill((150, 150, 150))
        G["SCREEN"].blit(IMAGES[name], (SX, SY))
        G["SCREEN"].blit(drawn_spritesheet_data(G, sheet, idx), (1072-256, 0))
        G["SCREEN"].blit(G["HEL32"].render("{}, {}".format((CX, CY), corner), 0, (200, 0, 80)), (1072, 840-32))
        pygame.draw.rect(G["SCREEN"], (255, 0, 0), Rect(make_rect((SX+corner[0], SY+corner[1]) if corner else (SX+CX+16, SY+CY+16), (SX+CX, SY+CY))), width=2)
        inp = expect_input()
        mods = pygame.key.get_mods()
        if inp == K_BACKSPACE: corner = None

        if mods & KMOD_CTRL:
            if inp == K_UP: idx = max(0, idx - 1) 
            if inp == K_DOWN: idx = min(len(keys), idx + 1)

        else:
            if inp == K_LEFT: CX -= 16 + (48 * mods & KMOD_SHIFT)
            if inp == K_UP: CY -= 16 + (48 * mods & KMOD_SHIFT)
            if inp == K_RIGHT: CX += 16 + (48 * mods & KMOD_SHIFT)
            if inp == K_DOWN: CY += 16 + (48 * mods & KMOD_SHIFT)

        if inp == K_a: SX -= 16 + (48 * mods & KMOD_SHIFT)
        if inp == K_w: SY -= 16 + (48 * mods & KMOD_SHIFT)
        if inp == K_d: SX += 16 + (48 * mods & KMOD_SHIFT)
        if inp == K_s: SY += 16 + (48 * mods & KMOD_SHIFT)

        if inp == K_ESCAPE:
            return

        if inp == K_s and mods & KMOD_CTRL:
            save()

        if inp == K_SPACE and mods & KMOD_CTRL:
            if idx < len(keys):
                pos, dim = sheet[keys[idx]]
                CX, CY = pos
                corner = pos[0] + dim[0], pos[1] + dim[1]
        
        elif inp == K_SPACE:
            corner = (CX, CY)

        if inp == K_RETURN:
            if idx < len(keys):
                sheet[keys[idx]] = make_rect(corner, (CX, CY))
            elif corner is not None:
                sheet[get_text_input(G, (0, 840-32))] = make_rect(corner, (CX, CY))
                keys = list(sheet.keys())

def save():
    global SAVED
    with open("src/rooms.py", "w+") as f:
        f.write("""ROOMS = {ROOMS}""".format(ROOMS=ROOMS))
    with open("src/actors.py", "w+") as f:
        f.write("""ACTORS = {ACTORS}""".format(ACTORS=ACTORS))
    with open("src/items.py", "w+") as f:
        f.write("""ITEMS = {ITEMS}""".format(ITEMS=ITEMS))

    with open("src/spritesheets.py", "w+") as f:
        f.write("""ROOM_SPRITESHEET = {ROOM_SPRITESHEET}
UX_SPRITESHEET = {UX_SPRITESHEET}
ACTOR_SPRITESHEET = {ACTOR_SPRITESHEET}
ITEM_SPRITESHEET = {ITEM_SPRITESHEET}
MOUSE_SPRITESHEET = {MOUSE_SPRITESHEET} 
""".format(ROOM_SPRITESHEET=ROOM_SPRITESHEET, UX_SPRITESHEET=UX_SPRITESHEET, ACTOR_SPRITESHEET=ACTOR_SPRITESHEET, ITEM_SPRITESHEET=ITEM_SPRITESHEET, MOUSE_SPRITESHEET=MOUSE_SPRITESHEET))
    SAVED = True
