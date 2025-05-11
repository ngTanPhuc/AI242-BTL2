import math
import random
import copy
import asyncio
from typing import Tuple, Set, List, Optional, Dict
from functools import lru_cache

# Config
class Config:
    GRID_SIZE = 9
    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    KOMI = 6.5
    CORNER_VALUE = 3.0
    EDGE_VALUE = 2.0
    CENTER_VALUE = 1.0

# Board (unchanged)
class Board:
    def __init__(self):
        self.board: List[List[int]] = [[0] * Config.GRID_SIZE for _ in range(Config.GRID_SIZE)]
        self.history: List[List[List[int]]] = []
        self.current_player: int = 1
        self.consecutive_passes: int = 0
        self.game_over: bool = False
        self.black_captures: int = 0
        self.white_captures: int = 0

    def print_board(self) -> None:
        print("  " + " ".join(str(i) for i in range(Config.GRID_SIZE)))
        for i, row in enumerate(self.board):
            row_str = " ".join("." if cell == 0 else "B" if cell == 1 else "W" for cell in row)
            print(f"{i} {row_str}")
        print(f"Black captures: {self.black_captures} | White captures: {self.white_captures}")

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE

    def is_empty(self, row: int, col: int) -> bool:
        return self.board[row][col] == 0

    @lru_cache(maxsize=1024)
    def get_group(self, row: int, col: int) -> Set[Tuple[int, int]]:
        if not self.is_valid_position(row, col) or self.board[row][col] == 0:
            return set()
        visited: Set[Tuple[int, int]] = set()
        player = self.board[row][col]

        def _recurse(r: int, c: int) -> None:
            if (not self.is_valid_position(r, c) or
                (r, c) in visited or
                self.board[r][c] != player):
                return
            visited.add((r, c))
            for dr, dc in Config.DIRECTIONS:
                _recurse(r + dr, c + dc)

        _recurse(row, col)
        return visited

    def has_liberties(self, group: Set[Tuple[int, int]], board: Optional[List[List[int]]] = None) -> bool:
        if board is None:
            board = self.board
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col) and board[new_row][new_col] == 0:
                    return True
        return False

    def get_eyes(self, group: Set[Tuple[int, int]]) -> List[Set[Tuple[int, int]]]:
        eyes = []
        visited = set(group)
        empty_adjacent = set()
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                    self.board[new_row][new_col] == 0 and
                    (new_row, new_col) not in visited):
                    empty_adjacent.add((new_row, new_col))

        for row, col in empty_adjacent:
            if (row, col) not in visited:
                empty_group = self.get_empty_group(row, col, visited)
                surrounded_by = self.get_surrounding_players(empty_group)
                first_row, first_col = next(iter(group))
                if surrounded_by == {self.board[first_row][first_col]}:
                    eyes.append(empty_group)
                visited.update(empty_group)
        return eyes

    def is_group_alive(self, group: Set[Tuple[int, int]]) -> bool:
        eyes = self.get_eyes(group)
        return len(eyes) >= 2 or any(len(eye) >= 4 for eye in eyes)

    def remove_dead_groups(self) -> None:
        if not self.game_over:
            return
        visited = set()
        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                if (row, col) not in visited and self.board[row][col] != 0:
                    group = self.get_group(row, col)
                    if not self.is_group_alive(group):
                        captured_count = len(group)
                        if self.board[row][col] == 1:
                            self.white_captures += captured_count
                        elif self.board[row][col] == 2:
                            self.black_captures += captured_count
                        for gr, gc in group:
                            self.board[gr][gc] = 0
                    visited.update(group)

    def get_territory(self) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        visited = set()
        black_territory = set()
        white_territory = set()

        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                if (row, col) not in visited and self.board[row][col] == 0:
                    empty_group, reaches_edge, surrounding_players = self.get_empty_group_status(row, col, visited)
                    if not reaches_edge:
                        if surrounding_players == {1}:
                            black_territory.update(empty_group)
                        elif surrounding_players == {2}:
                            white_territory.update(empty_group)
                    visited.update(empty_group)
        return black_territory, white_territory

    def get_empty_group_status(self, row: int, col: int, visited: set[tuple[int, int]]) -> tuple[set[tuple[int, int]], bool, set[int]]:
        group = set()
        reaches_edge = False
        surrounding_players = set()
        
        if not self.is_valid_position(row, col) or self.board[row][col] != 0 or (row, col) in visited:
            return group, reaches_edge, surrounding_players
        
        to_check = [(row, col)]
        while to_check:
            r, c = to_check.pop()
            if (r, c) in visited:
                continue
            group.add((r, c))
            visited.add((r, c))
            
            if r == 0 or r == Config.GRID_SIZE - 1 or c == 0 or c == Config.GRID_SIZE - 1:
                reaches_edge = True
                
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = r + dr, c + dc
                if self.is_valid_position(new_row, new_col):
                    if self.board[new_row][new_col] == 0 and (new_row, new_col) not in visited:
                        to_check.append((new_row, new_col))
                    elif self.board[new_row][new_col] != 0:
                        surrounding_players.add(self.board[new_row][new_col])
        return group, reaches_edge, surrounding_players

    def get_empty_group(self, row: int, col: int, visited: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        group = set()
        if not self.is_valid_position(row, col) or self.board[row][col] != 0 or (row, col) in visited:
            return group
        to_check = [(row, col)]
        while to_check:
            r, c = to_check.pop()
            if (r, c) in visited:
                continue
            group.add((r, c))
            visited.add((r, c))
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = r + dr, c + dc
                if (self.is_valid_position(new_row, new_col) and
                    self.board[new_row][new_col] == 0 and
                    (new_row, new_col) not in visited):
                    to_check.append((new_row, new_col))
        return group

    def get_surrounding_players(self, group: Set[Tuple[int, int]]) -> Set[int]:
        surrounding = set()
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] != 0:
                    surrounding.add(self.board[new_row][new_col])
        return surrounding

    def is_ko_violation(self, row: int, col: int, player: int) -> bool:
        if not self.history:
            return False
        temp_board = copy.deepcopy(self.board)
        temp_board[row][col] = player
        enemy = 3 - player
        captured = False
        for dr, dc in Config.DIRECTIONS:
            adj_row, adj_col = row + dr, col + dc
            if (self.is_valid_position(adj_row, adj_col) and
                temp_board[adj_row][adj_col] == enemy):
                group = self.get_group(adj_row, adj_col)
                if not self.has_liberties(group, temp_board):
                    captured = True
                    for gr, gc in group:
                        temp_board[gr][gc] = 0
        return captured and temp_board == self.history[-1]

    def can_place_stone(self, row: int, col: int) -> bool:
        return (self.is_valid_position(row, col) and
                self.is_empty(row, col) and
                not self.is_ko_violation(row, col, self.current_player) and
                not self.game_over)

    def place_stone(self, row: int, col: int) -> bool:
        if not self.can_place_stone(row, col):
            return False
        self.history.append(copy.deepcopy(self.board))
        self.board[row][col] = self.current_player
        self.consecutive_passes = 0
        enemy = 3 - self.current_player
        captured = False
        for dr, dc in Config.DIRECTIONS:
            adj_row, adj_col = row + dr, col + dc
            if (self.is_valid_position(adj_row, adj_col) and
                self.board[adj_row][adj_col] == enemy):
                group = self.get_group(adj_row, adj_col)
                if not self.has_liberties(group):
                    captured = True
                    captured_count = len(group)
                    if self.current_player == 1:
                        self.black_captures += captured_count
                    else:
                        self.white_captures += captured_count
                    for gr, gc in group:
                        self.board[gr][gc] = 0
        group = self.get_group(row, col)
        if not self.has_liberties(group):
            self.board[row][col] = 0
            self.history.pop()
            return False
        self.current_player = 3 - self.current_player
        return True

    def pass_turn(self) -> None:
        if self.game_over:
            return
        self.history.append(copy.deepcopy(self.board))
        self.consecutive_passes += 1
        if self.consecutive_passes >= 2:
            self.game_over = True
            self.remove_dead_groups()
        self.current_player = 3 - self.current_player

    def undo(self) -> None:
        if self.history and not self.game_over:
            self.board = copy.deepcopy(self.history.pop())
            self.current_player = 3 - self.current_player
            self.consecutive_passes = max(0, self.consecutive_passes - 1)

    def reset(self) -> None:
        self.board = [[0] * Config.GRID_SIZE for _ in range(Config.GRID_SIZE)]
        self.history.clear()
        self.current_player = 1
        self.consecutive_passes = 0
        self.game_over = False
        self.black_captures = 0
        self.white_captures = 0

    def calculate_score(self) -> Tuple[int, int]:
        black_territory, white_territory = self.get_territory()
        black_score = self.black_captures + len(black_territory)
        white_score = self.white_captures + len(white_territory) + Config.KOMI
        return black_score, white_score

    def get_winner(self) -> str:
        if not self.game_over:
            return "Game in progress"
        black_score, white_score = self.calculate_score()
        if black_score > white_score:
            return f"Black wins by {black_score - white_score} points"
        elif white_score > black_score:
            return f"White wins by {white_score - black_score} points"
        else:
            return "Draw"

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        moves = []
        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                if self.can_place_stone(row, col):
                    moves.append((row, col))
        random.shuffle(moves)
        return moves

# GameController (unchanged)
class GameController:
    def __init__(self, board: Board):
        self.board = board

    def make_move(self, row: int, col: int) -> bool:
        if self.board.game_over:
            return False
        return self.board.place_stone(row, col)

    def pass_turn(self) -> None:
        if not self.board.game_over:
            self.board.pass_turn()

    def undo(self) -> None:
        self.board.undo()

    def reset(self) -> None:
        self.board.reset()

    def get_score(self) -> Tuple[int, int]:
        return self.board.calculate_score()

    def get_winner(self) -> str:
        return self.board.get_winner()

    def is_game_over(self) -> bool:
        return self.board.game_over

class Minimax:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.transposition_table = {}

    def evaluate_position(self, row: int, col: int) -> float:
        if (row == 0 or row == Config.GRID_SIZE - 1) and (col == 0 or col == Config.GRID_SIZE - 1):
            return Config.CORNER_VALUE
        elif row == 0 or row == Config.GRID_SIZE - 1 or col == 0 or col == Config.GRID_SIZE - 1:
            return Config.EDGE_VALUE
        return Config.CENTER_VALUE

    def get_move_heuristic(self, move: Tuple[int, int]) -> float:
        row, col = move
        return self.evaluate_position(row, col)

    def evaluate_board(self, board: Board) -> float:
        black_score, white_score = board.calculate_score()
        base_score = black_score - white_score if board.current_player == 1 else white_score - black_score

        liberties_bonus = 0
        position_bonus = 0
        connectivity_bonus = 0
        threat_bonus = 0
        group_size_bonus = 0

        groups = {}
        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                if board.board[row][col] != 0 and (row, col) not in groups:
                    group = board.get_group(row, col)
                    groups.update({(r, c): group for r, c in group})
                    liberties = sum(1 for r, c in group for dr, dc in Config.DIRECTIONS
                                    if board.is_valid_position(r + dr, c + dc) and board.board[r + dr][c + dc] == 0)
                    player = board.board[row][col]
                    player_factor = 1 if player == board.current_player else -1
                    liberties_bonus += liberties * player_factor * 0.5
                    position_bonus += sum(self.evaluate_position(r, c) for r, c in group) * player_factor * 0.3
                    for r, c in group:
                        for dr, dc in Config.DIRECTIONS:
                            nr, nc = r + dr, c + dc
                            if board.is_valid_position(nr, nc) and board.board[nr][nc] == player:
                                connectivity_bonus += 0.4 * player_factor
                    if liberties <= 2 and player != board.current_player:
                        threat_bonus += 2.0 * player_factor
                    group_size_bonus += len(group) * player_factor * 0.2

        return (base_score + liberties_bonus + position_bonus + connectivity_bonus + threat_bonus + group_size_bonus)

    async def minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[float, Optional[Tuple[int, int]]]:
        board_tuple = tuple(map(tuple, board.board))
        if board_tuple in self.transposition_table:
            return self.transposition_table[board_tuple], None

        if depth == 0 or board.game_over:
            eval_score = self.evaluate_board(board)
            self.transposition_table[board_tuple] = eval_score
            return eval_score, None

        legal_moves = board.get_legal_moves()
        if not legal_moves:
            board.pass_turn()
            eval_score = self.evaluate_board(board)
            board.undo()
            self.transposition_table[board_tuple] = eval_score
            return eval_score, None

        legal_moves.sort(key=self.get_move_heuristic, reverse=True)

        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                new_board = copy.deepcopy(board)
                new_board.place_stone(*move)
                eval_score, _ = await self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            self.transposition_table[board_tuple] = max_eval
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_board = copy.deepcopy(board)
                new_board.place_stone(*move)
                eval_score, _ = await self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            self.transposition_table[board_tuple] = min_eval
            return min_eval, best_move

    async def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        print("AI đang suy nghĩ...")
        _, best_move = await self.minimax(board, self.depth, float('-inf'), float('inf'), board.current_player == 2)
        print("AI đã chọn xong.")
        return best_move

# RandomAI (unchanged)
class RandomAI:
    def __init__(self):
        pass

    async def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        legal_moves = board.get_legal_moves()
        if legal_moves:
            return random.choice(legal_moves)
        return None

# AIController (updated)
class AIController:
    def __init__(self, ai_type: str, depth: int = 3):
        if ai_type == "minimax":
            self.ai = Minimax(depth=depth)
        elif ai_type == "random":
            self.ai = RandomAI()
        else:
            raise ValueError("Loại AI không hợp lệ!")

    async def get_best_move(self, board: Board) -> Optional[Tuple[int, int]]:
        return await self.ai.get_best_move(board)

# GoGame (updated)
class GoGame:
    def __init__(self):
        self.board = Board()
        self.controller = GameController(self.board)
        self.mode = None
        self.ai1 = None
        self.ai2 = None

    def select_mode(self) -> str:
        while True:
            mode = input("Chọn chế độ chơi (1: Player vs AI, 2: AI vs AI): ").strip()
            if mode in ["1", "2"]:
                return mode
            print("Chế độ không hợp lệ! Vui lòng chọn 1 hoặc 2.")

    def select_ai_and_depth(self, player: str) -> Tuple[str, int]:
        while True:
            ai_choice = input(f"Chọn loại AI cho {player} (1: Minimax, 2: Random): ").strip()
            if ai_choice in ["1", "2"]:
                if ai_choice == "1":
                    while True:
                        try:
                            depth = int(input(f"Chọn độ sâu cho {player} (2-5): "))
                            if 2 <= depth <= 5:
                                return "minimax", depth
                            print("Độ sâu phải từ 2 đến 5!")
                        except ValueError:
                            print("Vui lòng nhập số hợp lệ!")
                else:
                    return "random", 0  # Random AI không cần độ sâu
            print("Loại AI không hợp lệ! Vui lòng chọn 1 hoặc 2.")

    async def run(self) -> None:
        print("Chào mừng đến với Go Game!")
        print("Lệnh: 'place row col' (đặt quân), 'pass', 'undo', 'reset', 'quit'")
        print("Ví dụ: 'place 3 3' để đặt quân tại hàng 3, cột 3")

        self.mode = self.select_mode()

        if self.mode == "1":  # Player vs AI
            ai_type, depth = self.select_ai_and_depth("AI")
            self.ai1 = AIController(ai_type, depth)
            print(f"Đã chọn AI: {ai_type}, độ sâu: {depth if ai_type == 'minimax' else 'N/A'}")
        elif self.mode == "2":  # AI vs AI
            ai_type1, depth1 = self.select_ai_and_depth("AI1")
            ai_type2, depth2 = self.select_ai_and_depth("AI2")
            self.ai1 = AIController(ai_type1, depth1)
            self.ai2 = AIController(ai_type2, depth2)
            print(f"Đã chọn AI1: {ai_type1}, độ sâu: {depth1 if ai_type1 == 'minimax' else 'N/A'}")
            print(f"Đã chọn AI2: {ai_type2}, độ sâu: {depth2 if ai_type2 == 'minimax' else 'N/A'}")

        while True:
            self.board.print_board()
            current_player = "Black" if self.board.current_player == 1 else "White"
            black_score, white_score = self.controller.get_score()
            print(f"Người chơi hiện tại: {current_player}")
            print(f"Điểm: Black: {black_score} | White: {white_score}")

            if self.controller.is_game_over():
                print("GAME OVER!!!")
                print(self.controller.get_winner())
                break

            if self.mode == "1":  # Player vs AI
                if self.board.current_player == 1:  # Người chơi (Black)
                    command = input("Nhập lệnh: ").strip().lower()
                    if command == "quit":
                        print("Đã thoát game!")
                        break
                    elif command == "pass":
                        self.controller.pass_turn()
                        print(f"{current_player} đã pass")
                    elif command == "undo":
                        self.controller.undo()
                        print("Đã hoàn tác nước đi trước")
                    elif command == "reset":
                        self.controller.reset()
                        print("Đã reset game")
                    elif command.startswith("place"):
                        try:
                            _, row, col = command.split()
                            row, col = int(row), int(col)
                            if self.controller.make_move(row, col):
                                print(f"{current_player} đặt quân tại ({row}, {col})")
                            else:
                                print("Nước đi không hợp lệ!")
                        except (ValueError, IndexError):
                            print("Lệnh không hợp lệ! Ví dụ: 'place 3 3'")
                    else:
                        print("Lệnh không xác định!")
                else:  # AI (White)
                    move = await self.ai1.get_best_move(self.board)
                    if move:
                        row, col = move
                        if self.controller.make_move(row, col):
                            print(f"AI (White) đặt quân tại ({row}, {col})")
                        else:
                            self.controller.pass_turn()
                            print("AI (White) đã pass")
                    else:
                        self.controller.pass_turn()
                        print("AI (White) đã pass")
            elif self.mode == "2":  # AI vs AI
                ai = self.ai1 if self.board.current_player == 1 else self.ai2
                move = await ai.get_best_move(self.board)
                if move:
                    row, col = move
                    if self.controller.make_move(row, col):
                        print(f"AI {current_player} đặt quân tại ({row}, {col})")
                    else:
                        self.controller.pass_turn()
                        print(f"AI {current_player} đã pass")
                else:
                    self.controller.pass_turn()
                    print(f"AI {current_player} đã pass")

# Main
if __name__ == "__main__":
    game = GoGame()
    asyncio.run(game.run())