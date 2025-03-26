# simulate_game.py
import pygame
from main import GoGame
from game_controller import GameController

def simulate_game_with_ui():

    game = GoGame()
    controller = game.controller

    def display_and_wait(message: str):
        print(message)
        game.renderer.render(game.board.board, controller.get_score(),
                             controller.is_game_over(), controller.get_winner())
        pygame.display.flip()


        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()


    display_and_wait("Bước 1: Trạng thái ban đầu. Nhấn Space hoặc Enter để tiếp tục...")


    controller.make_move(3, 3)
    display_and_wait("Bước 2: Đen đặt quân tại (3, 3). Nhấn Space hoặc Enter để tiếp tục...")


    controller.make_move(3, 4)
    display_and_wait("Bước 3: Trắng đặt quân tại (3, 4). Nhấn Space hoặc Enter để tiếp tục...")


    controller.make_move(4, 3)
    display_and_wait("Bước 4: Đen đặt quân tại (4, 3). Nhấn Space hoặc Enter để tiếp tục...")


    controller.pass_turn()
    display_and_wait("Bước 5: Đen pass. Nhấn Space hoặc Enter để tiếp tục...")


    controller.pass_turn()
    display_and_wait("Bước 6: Trắng pass (game kết thúc). Nhấn Space hoặc Enter để tiếp tục...")


    controller.undo()
    display_and_wait("Bước 7: Hoàn tác (undo). Nhấn Space hoặc Enter để tiếp tục...")


    controller.reset()
    display_and_wait("Bước 8: Đặt lại bàn cờ (reset). Nhấn Space hoặc Enter để kết thúc...")


if __name__ == "__main__":
    simulate_game_with_ui()