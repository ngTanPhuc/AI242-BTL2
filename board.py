
import copy
from typing import Tuple, Set, List, Optional
from config import Config

class Board:
    def __init__(self):
        self.board: List[List[int]] = [[0] * Config.GRID_SIZE for _ in range(Config.GRID_SIZE)]
        self.history: List[List[List[int]]] = []
        self.current_player: int = 1
        self.consecutive_passes: int = 0
        self.game_over: bool = False
        self.black_captures: int = 0
        self.white_captures: int = 0

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE

    def is_empty(self, row: int, col: int) -> bool:
        return self.board[row][col] == 0

    def get_group(self, row: int, col: int, board: Optional[List[List[int]]] = None) -> Set[Tuple[int, int]]:
        if board is None:
            board = self.board
        visited: Set[Tuple[int, int]] = set()
        if not self.is_valid_position(row, col) or board[row][col] == 0:
            return visited

        def _recurse(r: int, c: int, player: int) -> None:
            if (not self.is_valid_position(r, c) or
                (r, c) in visited or
                board[r][c] != player):
                return
            visited.add((r, c))
            for dr, dc in Config.DIRECTIONS:
                _recurse(r + dr, c + dc, player)

        _recurse(row, col, board[row][col])
        return visited

    def has_liberties(self, group: Set[Tuple[int, int]], board: Optional[List[List[int]]] = None) -> bool:
        if board is None:
            board = self.board
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                    board[new_row][new_col] == 0):
                    return True
        return False

    def get_eyes(self, group: Set[Tuple[int, int]], board: Optional[List[List[int]]] = None) -> List[Set[Tuple[int, int]]]:
        if not group:
            return []
        if board is None:
            board = self.board
        eyes = []
        visited = set(group)

        empty_adjacent = set()
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                    board[new_row][new_col] == 0 and
                    (new_row, new_col) not in visited):
                    empty_adjacent.add((new_row, new_col))

        for row, col in empty_adjacent:
            if (row, col) not in visited:
                empty_group = self.get_empty_group(row, col, visited)
                surrounded_by = self.get_surrounding_players(empty_group)
                first_row, first_col = next(iter(group))
                if surrounded_by == {board[first_row][first_col]}:
                    eyes.append(empty_group)
                visited.update(empty_group)

        return eyes

    def is_group_alive(self, group: Set[Tuple[int, int]]) -> bool:

        eyes = self.get_eyes(group)
        if len(eyes) >= 1:
            return True


        empty_adjacent = set()
        for row, col in group:
            for dr, dc in Config.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (self.is_valid_position(new_row, new_col) and
                    self.board[new_row][new_col] == 0 and
                    (new_row, new_col) not in empty_adjacent):
                    empty_adjacent.add((new_row, new_col))

        visited = set(group)
        empty_groups = []
        for row, col in empty_adjacent:
            if (row, col) not in visited:
                empty_group = self.get_empty_group(row, col, visited)
                empty_groups.append(empty_group)
                visited.update(empty_group)


        for empty_group in empty_groups:
            if len(empty_group) >= 4:
                surrounded_by = self.get_surrounding_players(empty_group)
                first_row, first_col = next(iter(group))
                if surrounded_by == {self.board[first_row][first_col]}:
                    return True

        return False

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

    def get_territory(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        visited = set()
        black_territory = set()
        white_territory = set()

        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                if (row, col) not in visited and self.board[row][col] == 0:
                    empty_group = self.get_empty_group(row, col, visited)
                    surrounded_by = self.get_surrounding_players(empty_group)
                    if surrounded_by == {1}:
                        black_territory.update(empty_group)
                    elif surrounded_by == {2}:
                        white_territory.update(empty_group)
                    visited.update(empty_group)

        return black_territory, white_territory

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
                if (self.is_valid_position(new_row, new_col) and
                    self.board[new_row][new_col] != 0):
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
                group = self.get_group(adj_row, adj_col, temp_board)
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