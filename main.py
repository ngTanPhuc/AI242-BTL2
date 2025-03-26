
import pygame
from typing import Tuple
from config import Config
from board import Board
from render import Renderer
from game_controller import GameController

class GoGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Go Game - Pygame")
        self.clock = pygame.time.Clock()

        self.board = Board()
        self.controller = GameController(self.board)
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = self.get_cell_from_mouse(event.pos)
                    self.controller.make_move(row, col)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.controller.undo()
                    elif event.key == pygame.K_r:
                        self.controller.reset()
                    elif event.key == pygame.K_p:
                        self.controller.pass_turn()

            self.renderer.render(self.board.board, self.controller.get_score(),
                                 self.controller.is_game_over(), self.controller.get_winner())
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = GoGame()
    game.run()