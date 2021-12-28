# Refactoring a demo O-0
import pygame
pygame.init()

from src.game import setup_game, run_game

if __name__ == "__main__":
    G = setup_game()
    run_game(G)
    
