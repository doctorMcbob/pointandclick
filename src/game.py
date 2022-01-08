import pygame
from pygame import Surface, Rect

from src.utils import expect_click, load_spritesheet
from src.spritesheets import ROOM_SPRITESHEET, UX_SPRITESHEET, ACTOR_SPRITESHEET, ITEM_SPRITESHEET, MOUSE_SPRITESHEET
from src.rooms import ROOMS
from src.actors import ACTORS
from src.items import ITEMS

import sys

TITLE="Point And Click Adventure Game Jam"

STARTING_ROOM = "ROOT" if '-r' not in sys.argv else sys.argv[sys.argv.index('-r') + 1]

SHOW_INV = False

BUTTONS = {
    "INVBUTTON": ((1072-64, 640 - 64), (64, 64))
}

def resolve(G, cmd):
    verb, data = cmd.split("|", 1)

    if verb == "say":
        imgid, text = data.split(":")
        say(G, imgid, text)

    elif verb == "unlock":
        room, lockid = data.split(":")
        if lockid in ROOMS[room]["LOCKS"]:
            ROOMS[room]["LOCKS"].pop(lockid)

    elif verb == "give":
        G["INV"].append(data)

    elif verb == "update":
        actor, state = data.split(":")
        ACTORS[actor]["STATE"] = state

    elif verb == "goto":
        G["ROOM"] = data

    elif verb == "change":
        actor, state, name = data.split(":")
        ACTORS[actor][name] = ACTORS[actor][state]

    elif verb == "img":
        actor, image = data.split(":")
        ACTORS[actor]["IMG"] = image

    elif verb == "put":
        room, item = data.split(":")
        ROOMS[room]["ITEMS"].append(item)

    elif verb == "place":
        room, actor = data.split(":")
        ROOMS[room]["ACTORS"].append(actor)

    elif verb == "drop":
        room, name = data.split(":")
        if name in ROOMS[room]["ITEMS"]: ROOMS[room]["ITEMS"].remove(name)
        if name in ROOMS[room]["ACTORS"]: ROOMS[room]["ACTORS"].remove(name)

    elif verb == "exec":
        actor, state = data.split(":")
        if state in ACTORS[actor]:
            for cmd in ACTORS[actor][state]:
                resolve(G, cmd)
                

def say(G, image_id, text):
    def _say(G):
        click_draw(G)
        surf = Surface((640, 256))
        surf.fill((1, 255, 1))
        actor = Surface((160, 230))
        actor.fill((255, 255, 255))
        actor.blit(G["ACTORIMG"][image_id], (0, 5))
        surf.blit(actor, (28, 23-5))
        surf.blit(G["SYSIMG"]["SAY"], (0, 0))
        for i, line in enumerate(text.split("/")):
            surf.blit(G["HEL32"].render(line, 0, (0, 0, 0)), (229, 22 + i*34))
        surf.set_colorkey((1, 255, 1))
        G["SCREEN"].blit(surf, (220, 640 - 256 - 64))
    expect_click(G, _say)

def draw(G, mouse_pos=None):
    room = ROOMS[G["ROOM"]]
    G["SCREEN"].blit(G["ROOMIMG"][room["IMG"]], (0, 0))

    for name in room["ACTORS"]:
        actor = ACTORS[name]
        pos, dim = actor["RECT"]
        G["SCREEN"].blit(G["ACTORIMG"][actor["IMG"]], pos)
        
    for name in room["ITEMS"]:
        item = ITEMS[name]
        pos, dim = item["RECT"]
        G["SCREEN"].blit(G["ITEMIMG"][item["IMG"]], pos)

    pos, dim = BUTTONS["INVBUTTON"]
    G["SCREEN"].blit(G["SYSIMG"]["INVBUTTON"], pos)
    if SHOW_INV:
        idx = (mouse_pos[1] - 48) // 48 if mouse_pos is not None and mouse_pos[0] > 1072-256 else None

        G["SCREEN"].blit(drawn_inventory(G, idx), (1072 - 256, 0))

def drawn_inventory(G, idx=None):
    inv = G["INV"]
    surf = pygame.Surface((256, 480))
    surf.fill((1, 255, 1))
    surf.blit(G["SYSIMG"]["INVTOP"], (0, 0))
    surf.blit(G["SYSIMG"]["INVBOT"], (0, 480-48))
    
    for i in range(8):
        if i == 0:
            surf.blit(G["SYSIMG"]["INVTOPSLOT"], (0, 48 + i * 48))
        elif i == 7:
            surf.blit(G["SYSIMG"]["INVBOTSLOT"], (0, 48 + i * 48))
        else:
            surf.blit(G["SYSIMG"]["INVSLOT"], (0, 48 + i * 48))
    for i, item in enumerate(inv):
        col = (50, 160, 85) if idx == i else (0, 0, 0)
        surf.blit(G["HEL32"].render(item, 0, col), (8, 48 + 8 + i * 48))
    surf.set_colorkey((1, 255, 1))
    return surf

def setup_game():
    G = {
        "SCREEN": pygame.display.set_mode((1072, 640)),
        "HEL32": pygame.font.SysFont("Helvetica", 32),
        "CLOCK": pygame.time.Clock(),
        
        "INV": [],
        "ROOM": STARTING_ROOM,
        
        "ROOMIMG": load_spritesheet("rooms.png", ROOM_SPRITESHEET),
        "SYSIMG": load_spritesheet("menu.png",  UX_SPRITESHEET),
        "ACTORIMG": load_spritesheet("actor.png",  ACTOR_SPRITESHEET),
        "MOUSEIMG": load_spritesheet("mouse.png", MOUSE_SPRITESHEET),
        "ITEMIMG" : load_spritesheet("items.png", ITEM_SPRITESHEET),
    }
    pygame.display.set_caption(TITLE)
    return G

def item_click(G, name):
    global SHOW_INV
    SHOW_INV = False
    def _draw(G):
        pos = pygame.mouse.get_pos()
        item = ITEMS[name]
        click_draw(G)
        G["SCREEN"].blit(G["ITEMIMG"][item["IMG"]], (pos[0] - 32, pos[1] - 32))
    return expect_click(G, _draw)
        
def click_draw(G):
    pos = pygame.mouse.get_pos()
    draw(G, pos)
    pygame.mouse.set_visible(False)

    room = ROOMS[G["ROOM"]]
    mouse = "X"
    for name in ACTORS:
        actor = ACTORS[name]
        if name not in room["ACTORS"]: continue
        if "MOUSE" not in actor: continue
        if Rect(actor["RECT"]).collidepoint(pos):
            mouse = actor["MOUSE"]
    for name in room["EXITS"]:
        ex = room["EXITS"][name]
        if "MOUSE" not in ex: continue
        if Rect(ex["RECT"]).collidepoint(pos):
            mouse = ex["MOUSE"]
    for name in ITEMS:
        item = ITEMS[name]
        if name not in room["ITEMS"]: continue
        if "MOUSE" not in item: continue
        if Rect(item["RECT"]).collidepoint(pos):
            mouse = item["MOUSE"]
    G["SCREEN"].blit(G["MOUSEIMG"][mouse], (pos[0]-8, pos[1]-8))

def run_game(G):
    global SHOW_INV
    while True:
        room = ROOMS[G["ROOM"]]
        draw(G)
        pygame.display.update()
        pos = expect_click(G, click_draw)

        if Rect(BUTTONS["INVBUTTON"]).collidepoint(pos):
            SHOW_INV = not SHOW_INV

        if SHOW_INV and pos[0] > 1072 - 256 and pos[1] < 480:
            idx = (pos[1] - 48) // 48
            if G["INV"] and idx < len(G["INV"]):
                item = G["INV"][idx]
                pos = item_click(G, G["INV"][idx])
                if pos:
                    for name in room["ACTORS"]:
                        actor = ACTORS[name]
                        if item in actor and Rect(actor["RECT"]).collidepoint(pos):
                            for cmd in actor[item]:
                                resolve(G, cmd)
                            G["INV"].remove(item)

                    for lockid in list(room["LOCKS"].keys()):
                        lock = room["LOCKS"][lockid]
                        if "KEY" in lock and lock["KEY"] == G["INV"][idx]:
                            target = lock["TARGET"]
                            if (target in room["ITEMS"] and Rect(ITEMS[target]["RECT"]).collidepoint(pos)
                            ) or (target in room["EXITS"] and Rect(room["EXITS"][target]["RECT"]).collidepoint(pos)):
                                room["LOCKS"].pop(lockid)
                                G["INV"].pop(idx)
                                if "CMDS" in lock:
                                    for cmd in lock["CMDS"]:
                                        resolve(G, cmd)
                                break
        else:
            for name in room["ACTORS"]:
                actor = ACTORS[name]
                if Rect(actor["RECT"]).collidepoint(pos):
                    for cmd in actor[actor["STATE"]]:
                        resolve(G, cmd)
                        
            for name in room["EXITS"]:
                if any(room["LOCKS"][lockid]["TARGET"] == name for lockid in room["LOCKS"]):
                    continue

                ex = room["EXITS"][name]
                if Rect(ex["RECT"]).collidepoint(pos):
                    G["ROOM"] = name

            for name in room["ITEMS"]:
                if any(room["LOCKS"][lockid]["TARGET"] == name for lockid in room["LOCKS"]):
                    continue

                item = ITEMS[name]
                if Rect(item["RECT"]).collidepoint(pos):
                    if "CMDS" in item:
                        for cmd in item["CMDS"]:
                            resolve(cmd)
                    else:
                        G["INV"].append(name)
                        room["ITEMS"].remove(name)
