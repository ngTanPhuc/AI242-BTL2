
class Config:
    GRID_SIZE = 19
    CELL_SIZE = 30
    BOARD_SIZE = GRID_SIZE * CELL_SIZE
    SCORE_HEIGHT = 50
    WINDOW_WIDTH = BOARD_SIZE
    WINDOW_HEIGHT = BOARD_SIZE + SCORE_HEIGHT

    STONE_RADIUS = CELL_SIZE // 2 - 2
    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BOARD_COLOR = (199, 164, 108)
    GRAY = (150, 150, 150)
    BACKGROUND_COLOR = (200, 200, 200)
    KOMI = 6.5  # Traditional komi for White ( + KOMI score in white to cal who win game)