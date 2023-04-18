import pickle
from abc import ABC, abstractmethod
from itertools import repeat
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

GREEDY_SELECTION = False
SOFTMAX_TEMPERATURE = 0.1
LEARNING_RATE = 0.5
DISCOUNT_FACTOR = 0.85
TRAINING_DATA_REUSE = 5


def softmax(x, t=1):
    x = np.array(x) / t
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


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

        # https://en.wikipedia.org/wiki/Q-learning#Initial_conditions_(Q0)
        # The default reward for an action is 1. This promotes action exploration.
        action_values = self._action_values(normalized_game_state.code)

        if GREEDY_SELECTION:
            action_choice = max(action_values.keys(), key=action_values.get)
        else:
            # We use a softmax selection algorithm over the current expected rewards
            # from each possible action.
            action_codes = list(action_values.keys())
            action_rewards = list(map(action_values.get, action_codes))
            action_choice = np.random.choice(
                action_codes, p=softmax(action_rewards, t=SOFTMAX_TEMPERATURE)
            )

        # Apply the normalization inverse to the action so it matches the true game state.
        return Board.from_board_code(action_choice).transform(normalization_inverse)

    def load(self):
        if not self._save_path.exists():
            self._value_table = {}
            return

        with self._save_path.open("rb") as save_file:
            self._value_table = pickle.load(save_file)

    def save(self):
        with self._save_path.open("wb") as save_file:
            pickle.dump(self._value_table, file=save_file)

    def _action_values(self, state_code: int) -> Dict[int, float]:
        possible_action_codes = [
            action.code for action in Board.from_board_code(state_code).possible_actions
        ]
        action_values = self._value_table.get(state_code, {})

        # If a possible action has no expected value, we assume it to be 1.
        return {
            action_code: action_values.get(action_code, 1.0)
            for action_code in possible_action_codes
        }

    def _max_state_value(self, state_code: int) -> float:
        action_values = self._value_table.get(state_code, {})
        if len(action_values) == 0:
            # When there are no recorded values for this state, we default to a value
            # of 0.
            return 0.0

        return max(action_values.values())

    def train(self, data: List[Tuple[int, int, int, float]]):
        for _ in range(TRAINING_DATA_REUSE):
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
                    (reward + DISCOUNT_FACTOR * resultant_state_value)
                    - initial_state_value
                )

    @property
    def name(self) -> str:
        return "QLearning Agent"
