# game_controller.py
from typing import Tuple
from board import Board

class GameController:
    # cái này để điều khiển game Go
    def __init__(self, board: Board):
        self.board = board

    def make_move(self, row: int, col: int) -> bool:
        # đặt quân ở vị trí row, col
        # row, col là hàng và cột, kiểu 0-8 nếu bàn 9x9
        # trả về True nếu đặt được, False nếu không
        if self.board.game_over:  # game over thì không đặt được
            return False
        return self.board.place_stone(row, col)  # gọi hàm đặt quân

    def pass_turn(self) -> None:
        # pass lượt, nếu 2 người pass liên tiếp thì game over
        if not self.board.game_over:  # chỉ pass nếu game chưa kết thúc
            self.board.pass_turn()

    def undo(self) -> None:
        # quay lại nước đi trước, không dùng được nếu game over
        self.board.undo()

    def reset(self) -> None:
        # reset bàn cờ, xóa hết quân
        self.board.reset()

    def get_score(self) -> Tuple[int, int]:
        # lấy điểm của Đen và Trắng
        return self.board.calculate_score()

    def get_winner(self) -> str:
        # xem ai thắng, trả về string kiểu "Black wins by 5.5 points"
        # nếu game chưa xong thì trả "Game in progress"
        return self.board.get_winner()

    def is_game_over(self) -> bool:
        # check game over chưa, True là xong, False là chưa
        return self.board.game_over