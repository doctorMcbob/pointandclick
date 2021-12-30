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

SYS_KEYS = ["MOUSE", "IMG", "RECT", "STATE"]
COMMAND_TYPES = ["say", "unlock", "give", "update", "goto"]

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

        if inp == K_a and mods & KMOD_SHIFT:
            name = select_from_list(G, list(ACTORS.keys()), (0, 0))
            actor_editor(G, name)

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

def drawn_cmd(G, cmd, dpth=None):
    verb, data = cmd.split("|")
    data = data.split(":")
    
    surf = Surface((1027, 32))
    surf.fill((255, 215, 0) if (dpth == 1 and len(data) == 1) or (dpth == 2 and len(data) == 2)  else (130, 130, 250))
    
    pygame.draw.rect(surf, (255, 215, 0) if dpth == 0 else (130, 250, 130), Rect((0, 0), (64, 32)))
    surf.blit(G["HEL32"].render(verb, 0, (0, 0, 0)), (0, 0))

    if len(data) > 1:
        pygame.draw.rect(surf, (255, 215, 0) if dpth == 1 else (250, 130, 130), Rect((64, 0), (128+64, 32)))
        surf.blit(G["HEL32"].render(data[0], 0, (0, 0, 0)), (64, 0))
        surf.blit(G["HEL32"].render(data[1], 0, (0, 0, 0)), (256, 0))
    else:
        surf.blit(G["HEL32"].render(data[0], 0, (0, 0, 0)), (126, 0))
    return surf

def drawn_cmds(G, cmds, idx=None, ddx=None):
    surf = Surface((1027, (len(cmds)+1)*32))
    surf.fill((1, 255, 1))
    for i, cmd in enumerate(cmds):
        surf.blit(drawn_cmd(G, cmd, dpth=ddx if i == idx else None), (0, i * 32))
    if idx is not None:
        surf.blit(G["HEL32"].render("ADD...", 0, (200, 0, 120) if idx == len(cmds) else (0, 0, 0) ), (0, len(cmds)*32))
    surf.set_colorkey((1, 255, 1))
    return surf

def drawn_actor_data(G, actor, idx=None, ddx=None, offset=0):
    surf = Surface((1072, 512))
    surf.fill((200, 200, 200))
    y = offset
    i_ = 0
    for i, key in enumerate(actor.keys()):
        col = (200, 0, 120) if idx - (i+i_) == 0 else (0, 0, 0)
        surf.blit(G["HEL32"].render(key, 0, col), (0, y))
        if key not in SYS_KEYS:
            y += 32
            cmd_surf = drawn_cmds(G, actor[key], idx-(i+i_) if idx-(i+i_) >= 0 else None, ddx)
            surf.blit(cmd_surf, (8, y))
            y += cmd_surf.get_height()
            i_ += len(actor[key])
        else:
            surf.blit(G["HEL32"].render(str(actor[key]), 0, col), (256, y))
            y += 32
    if idx is not None:
        col = (200, 0, 120) if idx == len(list(actor.keys())) + sum(len(actor[key]) for key in filter(lambda key: key not in SYS_KEYS, list(actor.keys()))) else (0, 0, 0)
        surf.blit(G["HEL32"].render("ADD...", 0, col), (0, y))

    return surf

def index_actor(actor, keys, idx):
    i = 0
    for key in keys:
        if key not in SYS_KEYS:
            cmds = actor[key]
            for i_, cmd in enumerate(cmds):
                if i == idx:
                    return key, i-i_, i_
                i += 1

            if i == idx:
                return key, i - len(cmds), -1
            i += 1
        else:
            if i == idx:
                return key, i, 0
            i += 1
    return False, 0, 0
            
def actor_editor(G, name):
    # I am so sorry
    actor = ACTORS[name]
    keys = list(actor.keys())
    idx = 0
    ddx = 0
    offset = 0
    while True:
        draw(G)
        G["SCREEN"].blit(drawn_actor_data(G, actor, idx, ddx, offset), (256, 0))
        G["SCREEN"].blit(G["HEL32"].render("{}, {}, {}".format(idx, ddx, len(keys)), 0, (255, 0, 0)), (1072, 808))
        inp = expect_input()
        mods = pygame.key.get_mods()

        if inp == K_ESCAPE:
            return

        if mods & KMOD_SHIFT:
            if inp == K_DOWN: offset += 32
            if inp == K_UP: offset -= 32
        else:
            if inp == K_LEFT: ddx = max(0, ddx-1)
            if inp == K_UP: idx = max(0, idx-1)
            if inp == K_RIGHT: ddx = min(2, ddx+1)
            if inp == K_DOWN: idx = min(len(keys) + sum(len(actor[key]) for key in filter(lambda key: key not in SYS_KEYS, keys)), idx+1)

        if inp == K_RETURN:
            key, i_, d_ = index_actor(actor, keys, idx)

            if key:
                if key == "IMG":
                    img = select_from_list(G, list(G["ACTORIMG"].keys()), (0, 0))
                    if img:
                        actor["IMG"] = img
                        
                if key == "MOUSE":
                    mouse = select_from_list(G, list(G["MOUSEIMG"]), (0, 0))
                    if mouse:
                        actor["MOUSE"] = mouse
                    
                if key == "STATE":
                    state = get_text_input(G, (0, 808))
                    if state:
                        actor["STATE"] = state

                if key == "RECT":
                    def click_draw(G):
                        draw(G)
                        pos = pygame.mouse.get_pos()
                        G["SCREEN"].blit(G["ACTORIMG"][actor["IMG"]], pos)
                    
                    pos = expect_click(G, click_draw)
                    if pos:
                        actor["RECT"] = pos, G["ACTORIMG"][actor["IMG"]].get_size()

                if key not in SYS_KEYS:
                    if key and d_ != -1:
                        cmds = actor[key]
                        cmd = cmds[d_]
                    else:
                        cmd = select_from_list(G, COMMAND_TYPES, (0, 0))
                        if cmd:
                            if cmd == "say":
                                imgid = select_from_list(G, list(G["ACTORIMG"].keys()), (0, 0))
                                if imgid:
                                    text = get_text_input(G, (0, 808))
                                    if text:
                                        [key].append("{cmd}|{imgid}:{text}".format(cmd=cmd, imgid=imgid, text=text))
                                    
                            if cmd == "unlock":
                                room = select_from_list(G, list(ROOMS.keys()), (0, 0))
                                if room:
                                    lockid = select_from_list(G, [lockid for lockid in ROOMS[room]["LOCKS"]], (0, 0))
                                    if lockid:
                                        actor[key].append("{cmd}|{room}:{lockid}".format(cmd=cmd, room=room, lockid=lockid))
                                        
                            if cmd == "give":
                                item = select_from_list(G, list(ITEMS.keys()), (0, 0))
                                if item:
                                    actor[key].append("{cmd}|{item}".format(cmd=cmd, item=item))
                                    
                            if cmd == "update":
                                actor_name = select_from_list(G, list(ACTORS.keys()), (0, 0))
                                if actor:
                                    states = [key for key in filter(lambda key: key not in SYS_KEYS, list(ACTORS[actor_name].keys()))]
                                    state = select_from_list(G, states, (0, 0))
                                    if state:
                                        actor[key].append("{cmd}|{actor}:{state}".format(cmd=cmd, actor=actor_name, state=state))
                                        
                            if cmd == "goto":
                                room = select_from_list(G, list(ROOMS.keys()), (0, 0))
                                if room:
                                    actor[key].append("{cmd}|{room}".format(cmd=cmd, room=room))
                                
                        
                        

                    
            if idx == len(keys) + sum(len(actor[key]) for key in filter(lambda key: key not in SYS_KEYS, keys)):
                name = get_text_input(G, (0, 840-32))
                if name:
                    actor[name] = []
                    keys = list(actor.keys())

                                    
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
