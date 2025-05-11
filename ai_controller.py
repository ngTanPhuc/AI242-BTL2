# ai_controller.py
from ai_mcts import MCTS

class AIController:
    def __init__(self, level=5):
        simulations = 100 * level
        threads = 4 if level >= 7 else 2
        self.mcts = MCTS(num_simulations=simulations, threads=threads)

    async def get_best_move(self, board):
        return await self.mcts.search(board)