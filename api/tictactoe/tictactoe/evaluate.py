from pathlib import Path

import numpy as np
from tqdm import tqdm

from tictactoe.agent import Agent, QLearningAgent, RandomAgent
from tictactoe.states import SYMBOL_SWAP, Board

import pprint


def evaluate(rounds: int, agent1: Agent, agent2: Agent):
    wins = [0, 0, 0]
    for _ in tqdm(range(rounds), desc="Evaluating"):
        result = evaluate_game(agent1=agent1, agent2=agent2)

        # Record the results.
        wins[result] += 1

    print(f"{agent1.name} Wins: {wins[1]} ({100 * wins[1] / rounds}%)")
    print(f"{agent2.name} Wins: {wins[2]} ({100 * wins[2] / rounds}%)")
    print(f"Ties: {wins[0]} ({100 * wins[0] / rounds}%)")


def evaluate_game(agent1: Agent, agent2: Agent) -> int:
    np_board = np.zeros(shape=(3, 3), dtype=np.int64)

    # By convention, agent1 is X and goes first.
    agents = [agent1, agent2]
    agent_is_x = [True, False]
    turn = 0
    while True:
        # Get the agent's action and apply it
        np_action = (
            agents[turn % 2]
            .act(Board(np_board=np_board, agent_is_x=agent_is_x[turn % 2]))
            ._board
        )
        if not agent_is_x[turn % 2]:
            # Swap the player of the agent's action.
            np_action = np.vectorize(SYMBOL_SWAP.get)(np_action)

        np_board += np_action

        winner, tie = Board(np_board=np_board).win_condition
        if winner != 0:
            return winner
        if tie:
            return 0

        turn += 1


if __name__ == "__main__":
    agent_data = Path("../agent_data/agent_data.pickle")
    assert agent_data.exists()

    learning_agent = QLearningAgent(save_path=agent_data)
    pprint.pprint(learning_agent._value_table)
    # The QLearning agent is strictly the second agent for now, as the agent
    # is only trained to be player 2 for simplicty.
    evaluate(
        10000,
        agent1=RandomAgent(),
        agent2=learning_agent,
    )
