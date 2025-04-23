import pygame
from typing import Tuple, Optional

from ai_controller import AIController
from config import Config
from board import Board
from render import Renderer
from game_controller import GameController
from start_menu import StartMenu
from button import Button
import random


class GoGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Go Game - Pygame")
        self.clock = pygame.time.Clock()

        self.board = None
        self.controller = None
        self.renderer = None
        self.ai = None

    def get_cell_from_mouse(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        return (round((y - Config.CELL_SIZE // 2) / Config.CELL_SIZE),
                round((x - Config.CELL_SIZE // 2) / Config.CELL_SIZE))

    def draw_start_menu(self) -> Optional[int]:
        # Display Start Menu
        startMenu = StartMenu(self.screen, pygame.font.Font(None, 24))

        # Display buttons
        button_lst = []
        for i in range(10):
            row = i // Config.BUTTONS_PER_ROW
            col = i % Config.BUTTONS_PER_ROW

            x = Config.BUTTON_START_X + col * (Config.BUTTON_WIDTH + Config.BUTTON_SPACING_X)
            y = Config.BUTTON_START_Y + row * (Config.BUTTON_HEIGHT + Config.BUTTON_SPACING_Y)

            button = Button(self.screen, x, y, str(i + 1))
            button_lst.append(button)

        startMenu.draw_start_menu()
        for button in button_lst:
            button.draw_button()
            clicked = button.get_difficulty()
            if clicked is not None:
                return clicked

        return None

    def draw_game(self, difficulty) -> None:
        self.board = Board()
        self.controller = GameController(self.board)
        self.renderer = Renderer(self.screen, pygame.font.Font(None, 24))
        self.ai = AIController(difficulty)

    def run(self) -> None:
        is_start_menu = True
        running = True
        pass_turn = 0
        is_random_passed = False
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if is_start_menu:  # Start Menu
                difficulty = self.draw_start_menu()
                if difficulty is not None:
                    print("Choose difficulty:", difficulty)
                    self.draw_game(difficulty)
                    is_start_menu = False
            else:  # If a difficulty is chosen, start the game
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        row, col = self.get_cell_from_mouse(event.pos)
                        self.controller.make_move(row, col)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_u:
                            self.controller.undo()
                        elif event.key == pygame.K_r:
                            self.controller.reset()
                        elif event.key == pygame.K_p:
                            self.controller.pass_turn()

                # Random makes move
                if self.board.current_player == 1 and not self.controller.is_game_over():  # Random is Black
                    random_move = random.choice(self.board.get_legal_moves())
                    # print(f"Random1: {random_move}")
                    if random_move:
                        random_row = random_move[0]
                        random_col = random_move[1]
                        if not self.controller.make_move(random_row, random_col):
                            self.controller.pass_turn()
                            pass_turn += 1
                            is_random_passed = True
                            print("Random1 pass")
                        else:
                            pass_turn = 0
                            is_random_passed = False

                # AI makes move
                if self.board.current_player == 2 and not self.controller.is_game_over():  # AI is White
                    AI_move = self.ai.get_best_move(self.board)
                    black_score, white_score = self.controller.get_score()
                    if AI_move:
                        AI_row = AI_move[0]
                        AI_col = AI_move[1]
                        if (not self.controller.make_move(AI_row, AI_col) or
                                (white_score > black_score and is_random_passed)):
                            self.controller.pass_turn()
                            pass_turn += 1
                            print("AI Pass")
                        else:
                            pass_turn = 0

                # Check if 2 players passed turn
                if pass_turn == 2:
                    print("GAME OVER!!!")
                    self.board.game_over = True
                    print(self.board.get_winner())
                    running = False

                self.renderer.render(self.board.board, self.controller.get_score(),
                                     self.controller.is_game_over(), self.controller.get_winner())

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = GoGame()
    game.run()