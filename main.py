import pygame
from typing import Tuple
from config import Config
from board import Board
from render import Renderer


class GoGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Go Game - Pygame")
        self.clock = pygame.time.Clock()

        self.board = Board()
        self.renderer = Renderer(self.screen, pygame.font.Font(None, 24))

    def get_cell_from_mouse(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        return (round((y - Config.CELL_SIZE // 2) / Config.CELL_SIZE),
                round((x - Config.CELL_SIZE // 2) / Config.CELL_SIZE))

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.board.game_over:
                    row, col = self.get_cell_from_mouse(event.pos)
                    self.board.place_stone(row, col)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.board.undo()
                    elif event.key == pygame.K_r:
                        self.board.reset()
                    elif event.key == pygame.K_p and not self.board.game_over:
                        self.board.pass_turn()

            self.renderer.render(self.board.board, self.board.calculate_score(),
                                 self.board.game_over, self.board.get_winner())
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    GoGame().run()