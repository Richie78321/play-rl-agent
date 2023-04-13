import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from tictactoe.states import Board


class Agent(ABC):
    @abstractmethod
    def act(self, game_state: Board) -> Board:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
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

    @property
    def name(self) -> str:
        return "Random Agent"


StateActionTable = Dict[int, Dict[int, float]]

RANDOM_SELECTION_EPSILON = 0.1
LEARNING_RATE = 0.5
DISCOUNT_FACTOR = 0.99


class QLearningAgent(Agent):
    _save_path: Path
    _value_table: StateActionTable
    _random_agent: RandomAgent

    def __init__(self, save_path: Path):
        self._save_path = save_path
        self._random_agent = RandomAgent()
        self.load()

    def act(self, game_state: Board) -> Board:
        # Normalize the game state.
        normalization, normalization_inverse = game_state.normalization_transform
        normalized_game_state = game_state.transform(normalization)

        # We use an Epsilon-Greedy selection algorithm for now out of simplicity.
        # This could likely be improved in the future.
        action_values = self._value_table.get(normalized_game_state.code, {})
        if len(action_values) == 0 or np.random.choice(
            [True, False], p=[RANDOM_SELECTION_EPSILON, 1 - RANDOM_SELECTION_EPSILON]
        ):
            # Choose a random action
            return self._random_agent.act(game_state=game_state)

        # Choose the optimal action according to the current value table.
        optimal_action = max(action_values, key=action_values.get)

        # Apply the normalization inverse to the action so it matches the true game state.
        return Board.from_board_code(optimal_action).transform(normalization_inverse)

    def load(self):
        if not self._save_path.exists():
            self._value_table = {}
            return

        with self._save_path.open("rb") as save_file:
            self._value_table = pickle.load(save_file)

    def save(self):
        with self._save_path.open("wb") as save_file:
            pickle.dump(self._value_table, file=save_file)

    def _max_state_value(self, state_code: int) -> float:
        action_values = self._value_table.get(state_code, {})
        if len(action_values) == 0:
            # When there are no recorded values for this state, we default to a value
            # of 0.
            return 0.0

        return max(action_values.values())

    def train(self, data: List[Tuple[int, int, int, float]]):
        for initial_state_code, action_code, resultant_state_code, reward in data:
            self._value_table.setdefault(initial_state_code, {})
            resultant_state_value = self._max_state_value(resultant_state_code)
            initial_state_value = self._value_table[initial_state_code].get(
                action_code, 0.0
            )

            # https://en.wikipedia.org/wiki/Q-learning#Algorithm
            self._value_table[initial_state_code][
                action_code
            ] = initial_state_value + LEARNING_RATE * (
                reward + DISCOUNT_FACTOR * resultant_state_value - initial_state_value
            )

    @property
    def name(self) -> str:
        return "QLearning Agent"
