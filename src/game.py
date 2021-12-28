import pygame

from src.utils import expect_click

IMG_LOCATION="/img/"

TITLE="Point And Click Adventure Game Jam"

STARTING_ROOM = "ROOT"

ROOMS = {
    "ROOT" : {
        "IMG"    : pygame.Surface((1080, 640)),
        "ITEMS"  : {},
        "ACTORS" : {},
        "LOCKS"  : {},
        "EXITS"  : {},
    }
}

ROOMS[STARTING_ROOM]["IMG"].fill((255, 255, 255))
ROOM_SPRITESHEET = {}

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

def draw(G):
    room = ROOMS[G["ROOM"]]
    G["SCREEN"].blit(room["IMG"], (0, 0))
    for piece in list(room["ITEMS"].values()) + list(room["ACTORS"].values()):
        pos, dim = piece
        G["SCREEN"].blit(piece["IMG"], pos)

def drawn_inventory(G):
    inv = G["INV"]
    surf = pygame.Surface((640, 32 * len(inv)))
    surf.blit
    return surf

def setup_game():
    G = {}
    G["SCREEN"] = pygame.display.set_mode((1080, 640))
    G["HEL32"] = pygame.font.SysFont("Helvetica", 32)
    G["CLOCK"] = pygame.time.Clock()

    G["INV"] = []
    G["ROOM"] = STARTING_ROOM

    room_sprites = load_spritesheet("rooms.png", ROOM_SPRITESHEET)
    for room in ROOMS:
        if room in room_spritesheet:
            room["IMG"] = room_sprites[room]
    
    pygame.display.set_caption(TITLE)
    return G

def click_draw(G):
    draw(G)
    pygame.mouse.set_visible(False)
    pygame.draw.circle(G["SCREEN"], (100, 0, 0), pygame.mouse.get_pos(), 2)
    
def run_game(G):
    while True:
        draw(G)
        pygame.display.update()
        pos = expect_click(G, click_draw)

