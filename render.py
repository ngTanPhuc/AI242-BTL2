# renderer.py
import pygame
from typing import Tuple, List
from config import Config


class Renderer:
    def __init__(self, screen: pygame.Surface, font: pygame.font):
        self.screen = screen
        self.font = font

    def render(self, board: List[List[int]], score: Tuple[int, int], game_over: bool, winner: str) -> None:
        self.screen.fill(Config.BACKGROUND_COLOR)
        board_rect = pygame.Rect(0, 0, Config.BOARD_SIZE, Config.BOARD_SIZE)
        pygame.draw.rect(self.screen, Config.BOARD_COLOR, board_rect)

        self._draw_grid()
        self._draw_star_points()
        self._draw_stones(board)
        self._draw_score(score, game_over, winner)

    def _draw_grid(self) -> None:
        half_cell = Config.CELL_SIZE // 2
        for i in range(Config.GRID_SIZE):
            pos = i * Config.CELL_SIZE + half_cell
            pygame.draw.line(self.screen, Config.BLACK,
                             (half_cell, pos), (Config.BOARD_SIZE - half_cell, pos))
            pygame.draw.line(self.screen, Config.BLACK,
                             (pos, half_cell), (pos, Config.BOARD_SIZE - half_cell))

    def _draw_star_points(self) -> None:
        star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        for y, x in star_points:
            center = (x * Config.CELL_SIZE + Config.CELL_SIZE // 2,
                      y * Config.CELL_SIZE + Config.CELL_SIZE // 2)
            pygame.draw.circle(self.screen, Config.BLACK, center, 4)

    def _draw_stones(self, board: List[List[int]]) -> None:
        for y in range(Config.GRID_SIZE):
            for x in range(Config.GRID_SIZE):
                center = (x * Config.CELL_SIZE + Config.CELL_SIZE // 2,
                          y * Config.CELL_SIZE + Config.CELL_SIZE // 2)
                if board[y][x] == 1:
                    pygame.draw.circle(self.screen, Config.BLACK, center, Config.STONE_RADIUS)
                elif board[y][x] == 2:
                    pygame.draw.circle(self.screen, Config.WHITE, center, Config.STONE_RADIUS)
                    pygame.draw.circle(self.screen, Config.GRAY, center, Config.STONE_RADIUS, 1)

    def _draw_score(self, score: Tuple[int, int], game_over: bool, winner: str) -> None:
        black, white = score
        text_str = f"Black: {black}  White: {white}"
        if game_over:
            text_str += f" - {winner}"
        else:
            text_str += " - Game in progress"
        text = self.font.render(text_str, True, Config.BLACK)
        text_rect = text.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.BOARD_SIZE + Config.SCORE_HEIGHT // 2))
        self.screen.blit(text, text_rect)