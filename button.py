#button.py
import pygame
from config import Config
from typing import Optional


class Button:
    def __init__(self, screen: pygame.Surface, x, y, text):
        self.button_rect = None
        self.x = x
        self.y = y
        self.screen = screen
        self.text = text
        self.clicked = False

    def draw_button(self) -> None:
        self.button_rect = pygame.draw.rect(self.screen, Config.WHITE,
                                            (self.x, self.y, Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT))
        pygame.draw.rect(self.screen, Config.BLACK,
                         (self.x, self.y, Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT), 3)

        font = pygame.font.Font(None, 30)
        num = font.render(self.text, True, Config.BLACK)
        num_surface = num.get_rect(center=(self.x + Config.BUTTON_WIDTH // 2, self.y + Config.BUTTON_HEIGHT // 2))
        self.screen.blit(num, num_surface)

    def get_difficulty(self) -> Optional[int]:
        pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] is True and not self.clicked:
                self.clicked = True
                return int(self.text)

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
