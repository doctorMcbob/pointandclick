import pygame
from pygame import Surface, Rect

from src.utils import expect_click

IMG_LOCATION="src/img/"

TITLE="Point And Click Adventure Game Jam"

STARTING_ROOM = "ROOT"

ROOMS = {
    "ROOT" : {
        "IMG"    : None,
        "ITEMS"  : {},
        "ACTORS" : {},
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
    "INVSLOT": ((256, 0) , (256, 48)),
    
}

BUTTONS = {
    "INVBUTTON": ((1080-64, 640 - 64), (64, 64))
}

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
    G["SCREEN"].blit(room["IMG"], (0, 0))
    for piece in list(room["ITEMS"].values()) + list(room["ACTORS"].values()):
        pos, dim = piece
        G["SCREEN"].blit(piece["IMG"], pos)

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

    room_sprites = load_spritesheet("rooms.png", ROOM_SPRITESHEET)
    G["SYSIMG"] = load_spritesheet("menu.png",  UX_SPRITESHEET)
    for room in ROOMS:
        if room in ROOM_SPRITESHEET:
            ROOMS[room]["IMG"] = room_sprites[room]
    
    pygame.display.set_caption(TITLE)
    return G

def click_draw(G):
    pos = pygame.mouse.get_pos()
    draw(G, pos)
    pygame.mouse.set_visible(False)
    pygame.draw.circle(G["SCREEN"], (100, 0, 0), pos, 2)
    
def run_game(G):
    global SHOW_INV
    while True:
        draw(G)
        pygame.display.update()
        pos = expect_click(G, click_draw)

        if Rect(BUTTONS["INVBUTTON"]).collidepoint(pos):
            SHOW_INV = not SHOW_INV

        
