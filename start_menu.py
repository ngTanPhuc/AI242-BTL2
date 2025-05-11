#start_menu.py
import pygame
from board import Board
from config import Config
from button import Button

class StartMenu:
    def __init__(self, screen: pygame.Surface, font: pygame.font):
        self.screen = screen
        self.font = font

    def draw_start_menu(self) -> None:
        self.screen.fill(Config.BOARD_COLOR)

        # Display name
        display_name_font = pygame.font.Font(None, 80)
        display_name_surface = display_name_font.render("Go game!!!", True, Config.BLACK)
        display_name_rect = display_name_surface.get_rect(center=(Config.WINDOW_WIDTH // 2,
                                                                  Config.WINDOW_HEIGHT // 6))
        self.screen.blit(display_name_surface, display_name_rect)

        # Display select difficulties
        font = pygame.font.Font(None, 40)
        instruction = font.render("Select difficulty:", True, Config.BLACK)
        instruction_surface = instruction.get_rect(center=(Config.WINDOW_WIDTH // 2,
                                                           Config.WINDOW_HEIGHT // 6 + 50))
        self.screen.blit(instruction, instruction_surface)
