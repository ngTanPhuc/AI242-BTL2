import random
import copy
from board import Board

class GoAI:
    def __init__(self, difficulty=5):
        self.difficulty = difficulty  # cấp độ 1-10

    def get_valid_moves(self, board: Board) -> list:
        # Lấy các nước đi hợp lệ
        moves = []
        for row in range(len(board.board)):
            for col in range(len(board.board)):
                if board.can_place_stone(row, col):
                    moves.append((row, col))
        return moves

    def simulate_random_game(self, board: Board) -> int:
        # Mô phỏng 1 ván random cho tới khi kết thúc
        sim_board = copy.deepcopy(board)
        while not sim_board.game_over:
            moves = self.get_valid_moves(sim_board)
            if moves:
                move = random.choice(moves)
                sim_board.place_stone(*move)
            else:
                sim_board.pass_turn()
        black_score, white_score = sim_board.calculate_score()
        return 1 if black_score > white_score else 2

    def get_best_move(self, board: Board) -> tuple:
        # Tìm nước đi tốt nhất
        moves = self.get_valid_moves(board)
        if not moves:
            return None

        if self.difficulty <= 3:
            # Nếu cấp độ thấp → random luôn
            return random.choice(moves)

        # Nếu cấp độ cao → dùng mô phỏng nhiều hơn
        simulations = int(self.difficulty * 100)

        move_scores = {move: 0 for move in moves}
        for move in moves:
            for _ in range(simulations // len(moves)):
                sim_board = copy.deepcopy(board)
                sim_board.place_stone(*move)
                winner = self.simulate_random_game(sim_board)
                if winner == board.current_player:
                    move_scores[move] += 1

        best_move = max(move_scores, key=move_scores.get)
        return best_move
