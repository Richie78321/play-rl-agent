from abc import ABC, abstractmethod

import numpy as np

from states import Board


class Agent(ABC):
    @abstractmethod
    def act(self, game_state: Board) -> Board:
        pass


class RandomAgent(Agent):
    def act(self, game_state: Board) -> Board:
        # Get a matrix of the coordinates of all the empty positions on the board.
        empty_coordinates = np.array(np.where(game_state._board == 0)).transpose()
        if empty_coordinates.shape[0] == 0:
            raise ValueError("no possible actions to take in this state")

        # Choose a random set of coordinates for the action.
        choice_coordinates = empty_coordinates[
            np.random.choice(empty_coordinates.shape[0])
        ]

        # Create a board for this action.
        action = np.zeros(shape=(3, 3), dtype=np.int64)
        action[tuple(choice_coordinates)] = 1
        return Board(action, agent_is_x=True)
