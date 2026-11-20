"""Disclosure-first game integration. Companion must be opened explicitly."""
import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

def install_keyboard_fix(pygame, tools):
    """Track actual key events instead of sampling state inside each event."""
    from collections import defaultdict

    def event_loop(control):
        if not isinstance(control.keys, dict):
            control.keys = defaultdict(bool)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                control.done = True
            elif event.type == pygame.KEYDOWN:
                control.keys[event.key] = True
            elif event.type == pygame.KEYUP:
                control.keys[event.key] = False
            elif event.type == pygame.WINDOWFOCUSLOST:
                control.keys.clear()

    pygame.event.set_allowed(pygame.WINDOWFOCUSLOST)
    tools.Control.event_loop = event_loop

def main():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo('Mario educational demo', 'This game is part of a disclosed screen-sharing demo.\n\nOpen client.py separately and explicitly consent if you want screenshots shared. The game never starts sharing automatically.\n\nThe visible companion can continue after this game closes. Stop sharing from that window.')
    root.destroy()
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    game = base / 'vendor' / 'PythonSuperMario'
    os.chdir(game)
    sys.path.insert(0, str(game))
    from source.main import main as game_main
    import pygame
    from source import tools
    install_keyboard_fix(pygame, tools)
    try:
        game_main()
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
