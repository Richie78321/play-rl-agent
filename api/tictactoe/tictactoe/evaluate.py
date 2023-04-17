from pathlib import Path

import numpy as np
from tqdm import tqdm

from tictactoe.agent import Agent, QLearningAgent, RandomAgent
from tictactoe.states import SYMBOL_SWAP, Board

from typing import List, Tuple, NamedTuple

import pprint

def evaluate(rounds: int, agent1: Agent, agent2: Agent):
    wins = [0, 0, 0]
    for _ in tqdm(range(rounds), desc="Evaluating"):
        if np.random.choice([True, False]):
            agents = [agent1, agent2]
            result_mapping = {
                0: 0,
                1: 1,
                2: 2,
            }
        else:
            agents = [agent2, agent1]
            result_mapping = {
                0: 0,
                1: 2,
                2: 1,
            }

        result, _ = evaluate_game(agent1=agents[0], agent2=agents[1])
        result = result_mapping[result]
        wins[result] += 1

    print(f"{agent1.name} Wins: {wins[1]} ({100 * wins[1] / rounds}%)")
    print(f"{agent2.name} Wins: {wins[2]} ({100 * wins[2] / rounds}%)")
    print(f"Ties: {wins[0]} ({100 * wins[0] / rounds}%)")

class StepData(NamedTuple):
    agent_id: int
    state: Board
    resultant_state: Board
    action: Board
    reward: float

def evaluate_game(agent1: Agent, agent2: Agent) -> Tuple[int, List[StepData]]:
    np_board = np.zeros(shape=(3, 3), dtype=np.int64)

    episode_data = []

    # By convention, agent1 is X and goes first.
    agents = [agent1, agent2]
    agent_is_x = [True, False]
    turn = 0
    while True:
        agent_id = turn % 2

        # Get the agent's action and apply it
        action = (
            agents[agent_id]
            .act(Board(np_board=np_board, agent_is_x=agent_is_x[agent_id]))
        )
        np_action = action._board
        if not agent_is_x[agent_id]:
            # Swap the player of the agent's action.
            np_action = np.vectorize(SYMBOL_SWAP.get)(np_action)
        
        # Apply the action
        new_np_board = np_board + np_action
        winner, tie = Board(np_board=new_np_board).win_condition

        # Record step data
        step_data = StepData(
            agent_id=agent_id,
            state=Board(np_board=np_board),
            resultant_state=Board(np_board=new_np_board),
            action=action,
            reward=1.0 if winner == agent_id + 1 else 0.0,
        )
        episode_data.append(step_data)
        
        if winner != 0:
            return winner, episode_data
        if tie:
            return 0, episode_data

        turn += 1
        np_board = new_np_board


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
