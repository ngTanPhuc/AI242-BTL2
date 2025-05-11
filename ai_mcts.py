# ai_mcts.py
import asyncio
import math
import random
import copy
from board import Board
from config import Config

class MCTSNode:
    def __init__(self, board: Board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self):
        legal_moves = self.board.get_legal_moves()
        return len(self.children) >= len(legal_moves)

    def best_child(self, c_param=1.4):
        choices = [
            (child, child.wins / child.visits + c_param * math.sqrt(math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return max(choices, key=lambda x: x[1])[0]

async def simulate(board: Board):
    sim_board = copy.deepcopy(board)
    while not sim_board.game_over:
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            sim_board.pass_turn()
            continue
        move = random.choice(legal_moves)
        sim_board.place_stone(*move)
    black_score, white_score = sim_board.calculate_score()
    return 1 if (sim_board.current_player == 2 and black_score > white_score) or (sim_board.current_player == 1 and white_score > black_score) else 0

class MCTS:
    def __init__(self, num_simulations=500, threads=4):
        self.num_simulations = num_simulations
        self.threads = threads  # Không còn cần thiết với asyncio, nhưng giữ lại cho tương thích

    async def search(self, board: Board):
        root = MCTSNode(copy.deepcopy(board))

        # Chạy các mô phỏng không đồng bộ
        tasks = [self.simulate_once(root) for _ in range(self.num_simulations)]
        await asyncio.gather(*tasks)

        best_move = max(root.children, key=lambda c: c.visits).move
        return best_move

    async def simulate_once(self, root):
        node = root

        while node.children and node.is_fully_expanded():
            node = node.best_child()

        legal_moves = node.board.get_legal_moves()
        if legal_moves:
            move = random.choice(legal_moves)
            new_board = copy.deepcopy(node.board)
            new_board.place_stone(*move)
            child_node = MCTSNode(new_board, parent=node, move=move)
            node.children.append(child_node)
            node = child_node

        result = await simulate(node.board)
        self.backpropagate(node, result)

    def backpropagate(self, node, result):
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent