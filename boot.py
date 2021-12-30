# Refactoring a demo O-0
import pygame
import sys

if __name__ == "__main__":
    pygame.init()

    if "-e" in sys.argv:
        from src.editor import setup_editor, run_editor
        G = setup_editor()
        run_editor(G)

    else:
        from src.game import setup_game, run_game
        G = setup_game()
        run_game(G)

    
