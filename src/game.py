import pygame
from pygame import Surface, Rect

from src.utils import expect_click

IMG_LOCATION="src/img/"

TITLE="Point And Click Adventure Game Jam"

STARTING_ROOM = "ROOT"

ROOMS = {
    "ROOT" : {
        "IMG": "ROOT",
        "ITEMS"  : {},
        "ACTORS" : {
            "funGuy"  : {
                "RECT"   : ((196, 348), (112, 160)),
                "IMG"    : "funguyHappy",
                "MOUSE"  : "POINT",
                "CMDS"   : [
                    "say|funguyHappy:Hello Fren",
                    "say|funguyLaugh:What?/Were you expecting some/sort of tutorial?",
                    "say|funguyHappy:Nope./Nothing here but me.",
                    "say|funguySad:It's pretty lonely!"
                ]
            }
        },
        "LOCKS"  : {},
        "EXITS"  : {},
    }
}

SHOW_INV = False

ROOM_SPRITESHEET = {
    "ROOT":((0, 0), (1080, 640))
}
UX_SPRITESHEET = {
    "INVBUTTON":((0, 0), (64, 64)),
    "INVSLOT": ((640, 0) , (256, 48)),
    "SAY": ((1280, 0), (640, 256))
    
}
ACTOR_SPRITESHEET = {
    "funguyHappy" : ((0, 0), (112, 160)),
    "funguySad"   : ((112, 0), (112, 160)),
    "funguyLaugh" : ((224, 0), (112, 160)),
}
ITEM_SPRITESHEET = {}
MOUSE_SPRITESHEET = {
    "X"      : ((0, 0), (16, 16)),
    "POINT"  : ((16, 0), (16, 16)),
    "UP"     : ((32, 0), (16, 16)),
    "DOWN"   : ((48, 0), (16, 16)),
    "LEFT"   : ((64, 0), (16, 16)),
    "RIGHT"  : ((80, 0), (16, 16)),
}

BUTTONS = {
    "INVBUTTON": ((1080-64, 640 - 64), (64, 64))
}

def resolve(G, cmd):
    verb, data = cmd.split("|", 1)

    if verb == "say":
        imgid, text = data.split(":")
        say(G, imgid, text)

    elif verb == "unlock":
        room, lockid = data.split(":")
        ROOMS[room]["LOCKS"].remove(lockid)

    elif verb == "give":
        G["INV"].append(data)

    elif verb == "update":
        room, actor, new_cmds = data.split(":", 2)
        ROOMS[room]["ACTORS"][actor]["CMDS"] = new_cmds.split(",")

def say(G, image_id, text):
    def _say(G):
        click_draw(G)
        surf = Surface((640, 256))
        surf.fill((255, 255, 255))
        surf.blit(G["ACTORIMG"][image_id], (0, 0))
        surf.blit(G["SYSIMG"]["SAY"], (0, 0))
        for i, line in enumerate(text.split("/")):
            surf.blit(G["HEL32"].render(line, 0, (0, 0, 0)), (205, 20 + i*34))
        G["SCREEN"].blit(surf, (220, 640 - 256 - 64))
    expect_click(G, _say)

def load_spritesheet(filename, data, colorkey=(1, 255, 1)):
    """data should be dict with key: ((x, y), (w, h)), assumes w, h are 32, 32"""
    surf = pygame.image.load(IMG_LOCATION+filename).convert()
    sheet = {}
    for name in data:
        sprite = Surface(data[name][1])
        x, y = 0 - data[name][0][0], 0 - data[name][0][1]
        sprite.blit(surf, (x, y))
        sprite.set_colorkey(colorkey)
        sheet[name] = sprite
    return sheet

def draw(G, mouse_pos=None):
    room = ROOMS[G["ROOM"]]
    G["SCREEN"].blit(G["ROOMIMG"][room["IMG"]], (0, 0))

    for name in room["ACTORS"]:
        actor = room["ACTORS"][name]
        pos, dim = actor["RECT"]
        G["SCREEN"].blit(G["ACTORIMG"][actor["IMG"]], pos)
        
    for name in room["ITEMS"]:
        item = room["ITEMS"][name]
        pos, dim = item["RECT"]
        G["SCREEN"].blit(G["ITEMIMG"][item["IMG"]], pos)

    pos, dim = BUTTONS["INVBUTTON"]
    G["SCREEN"].blit(G["SYSIMG"]["INVBUTTON"], pos)
    if SHOW_INV:
        idx = mouse_pos[1] // 48 if mouse_pos is not None and mouse_pos[0] > 1080-256 else None
            
        G["SCREEN"].blit(drawn_inventory(G, idx), (1080 - 256, 0))


def drawn_inventory(G, idx=None):
    inv = G["INV"]
    surf = pygame.Surface((256, 560))
    surf.fill((255, 255, 255))
    for i in range(10):
        surf.blit(G["SYSIMG"]["INVSLOT"], (0, i * 48))
    for i, item in enumerate(inv):
        col = (0, 150, 0) if idx == i else (0, 0, 0)
        surf.blit(G["HEL32"].render(item, 0, (0, 0, 0)), (8, 8 + i * 48))
    return surf

def setup_game():
    G = {}
    G["SCREEN"] = pygame.display.set_mode((1080, 640))
    G["HEL32"] = pygame.font.SysFont("Helvetica", 32)
    G["CLOCK"] = pygame.time.Clock()

    G["INV"] = []
    G["ROOM"] = STARTING_ROOM

    G["ROOMIMG"] = load_spritesheet("rooms.png", ROOM_SPRITESHEET)
    G["SYSIMG"] = load_spritesheet("menu.png",  UX_SPRITESHEET)
    G["ACTORIMG"] = load_spritesheet("actor.png",  ACTOR_SPRITESHEET)
    G["MOUSEIMG"] = load_spritesheet("mouse.png", MOUSE_SPRITESHEET)
    G["ITEMIMG"] = {}

    pygame.display.set_caption(TITLE)
    return G

def click_draw(G):
    pos = pygame.mouse.get_pos()
    draw(G, pos)
    pygame.mouse.set_visible(False)

    room = ROOMS[G["ROOM"]]
    mouse = "X"
    for noun in ["ACTORS", "ITEMS", "EXITS"]:
        for name in room[noun]:
            if "MOUSE" in room[noun][name]:
                if Rect(room[noun][name]["RECT"]).collidepoint(pos):
                    mouse = room[noun][name]["MOUSE"]
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

        for name in room["ACTORS"]:
            actor = room["ACTORS"][name]
            if Rect(actor["RECT"]).collidepoint(pos):
                for cmd in actor["CMDS"]:
                    resolve(G, cmd)
