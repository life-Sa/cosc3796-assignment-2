"""Exercise keyboard events without desktop capture or real keyboard input."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).parent / 'vendor' / 'PythonSuperMario'))
import pygame
from source import tools
from launch_mario import install_keyboard_fix

class KeyboardTest(unittest.TestCase):
    def test_key_press_release_and_focus_loss(self):
        pygame.init()
        pygame.display.set_mode((100, 100))
        try:
            install_keyboard_fix(pygame, tools)
            control = tools.Control()
            for key in (pygame.K_RETURN, pygame.K_RIGHT, pygame.K_a):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
                control.event_loop()
                self.assertTrue(control.keys[key])
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key))
                control.event_loop()
                self.assertFalse(control.keys[key])
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
            pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
            control.event_loop()
            self.assertFalse(control.keys[pygame.K_LEFT])
        finally:
            pygame.quit()

if __name__ == '__main__':
    unittest.main()
