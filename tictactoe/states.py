import numpy as np

VALUE_TO_POSITION = {
    0: "-",
    1: "X",
    2: "O",
}
POSITION_TO_VALUE = {
    "-": 0,
    "X": 1,
    "O": 2,
}
SYMBOL_SWAP = {
    0: 0,
    1: 2,
    2: 1,
}

# All of the possible transformations that yield a board with an equivalent state.
# For example, rotating the board by 90 degrees does not change the state of the game.
BOARD_SYMMETRY_TRANSFORMS = [
    # Identity
    lambda x: x,
    # Rotation by 90 degrees
    lambda x: np.rot90(x),
    # Rotation by 180 degrees
    lambda x: np.rot90(x, 2),
    # Rotation by 270 degrees
    lambda x: np.rot90(x, 3),
    # Horizontal reflection
    lambda x: np.flipud(x),
    # Vertical reflection
    lambda x: np.fliplr(x),
    # Diagonal reflection
    lambda x: np.transpose(x),
    # Anti-diagonal reflection
    lambda x: np.rot90(np.flipud(x)),
]


class Board:
    _board: np.ndarray

    @classmethod
    def from_np_text_board(cls, text_board: np.ndarray, agent_is_x: bool = True):
        if text_board.shape == (9,):
            text_board = text_board.reshape((3, 3))

        return cls(
            np.vectorize(POSITION_TO_VALUE.get)(text_board).astype(np.int8),
            agent_is_x=agent_is_x,
        )

    @classmethod
    def from_board_code(cls, board_code: int):
        cell_values = list(str(board_code).zfill(9))
        np_board = np.array(cell_values).astype(np.int8).reshape((3, 3))
        return Board(np_board=np_board)

    @staticmethod
    def is_valid_np_board(board: np.ndarray) -> bool:
        if board.dtype != np.int8:
            return False
        if board.shape != (3, 3):
            return False
        if board.min() < 0 or board.max() > 2:
            return False

        return True

    @staticmethod
    def np_board_to_code(board: np.ndarray) -> int:
        return int("".join(map(str, board.flatten())))

    def __init__(self, np_board: np.ndarray, agent_is_x: bool = False):
        if not Board.is_valid_np_board(np_board):
            raise ValueError(f"invalid board")

        if not agent_is_x:
            # Board states are always represented with the agent as X.
            # If the agent is O, then swap the symbols.
            np_board = np.vectorize(SYMBOL_SWAP.get)(np_board)

        self._board = np_board

    def __str__(self):
        return "\n".join(
            [" ".join(map(VALUE_TO_POSITION.get, row)) for row in self._board]
        )

    @property
    def code(self):
        return Board.np_board_to_code(self._board)

    @property
    def normalization_transform(self):
        """Return the transform function that will normalize the board such that
        all symmetrical boards are the same.
        """
        all_transforms = [
            (transform, Board.np_board_to_code(transform(self._board)))
            for transform in BOARD_SYMMETRY_TRANSFORMS
        ]

        # Pick the transform that yields the minimum board code. Since all board
        # codes are unique, this ensures that all symmetrical boards are transformed
        # to the same equivalent board state.
        min_transform, _ = min(all_transforms, key=lambda x: x[1])
        return min_transform

    def transform(self, transform) -> "Board":
        return Board(np_board=transform(self._board))
