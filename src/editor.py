import pygame
from pygame.locals import *

from src.utils import expect_click

from src.spritesheets import ROOM_SPRITESHEET, UX_SPRITESHEET, ACTOR_SPRITESHEET, ITEM_SPRITESHEET, MOUSE_SPRITESHEET
from src.rooms import ROOMS
from src.actors import ACTORS
from src.items import ITEMS

SAVED = False

def setup_editor():
    G = {
        "SCREEN": pygame.display.set_mode((1080, 640))
        "HEL32": pygame.font.SysFont("Helvetica", 32)
        
    } 
    return G

def run_editor(G):
    while True:
        return

def save_game():
    global SAVED
    with open("/src/rooms.py", "w+") as f:
        f.write("""ROOMS = {ROOMS}""".format(ROOMS=ROOMS))
    with open("/src/actors.py", "w+") as f:
        f.write("""ACTORS = {ACTORS}""".format(ACTORS=ACTORS))
    with open("/src/items.py", "w+") as f:
        f.write("""ITEMS = {ITEMS}""".format(ITEMS=ITEMS))

    with open("/src/spritesheets.py") as f:
        f.write("""ROOM_SPRITESHEET = {ROOM_SPRITESHEET}
UX_SPRITESHEET = {UX_SPRITESHEET}
ACTOR_SPRITESHEET = {ACTOR_SPRITESHEET}
ITEM_SPRITESHEET = {ITEM_SPRITESHEET}
""".format(ROOM_SPRITESHEET=ROOM_SPRITESHEET, UX_SPRITESHEET=UX_SPRITESHEET, ACTOR_SPRITESHEET=ACTOR_SPRITESHEET, ITEM_SPRITESHEET=ITEM_SPRITESHEET))
    SAVED = True
