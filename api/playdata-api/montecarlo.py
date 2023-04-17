from pathlib import Path

from app import process_playdata_json
from playdatakafka import Kafka
from tictactoe.agent import Agent, QLearningAgent, RandomAgent
from tictactoe.evaluate import StepData, evaluate_game
from tictactoe.states import Board
from tqdm import tqdm


# TODO(richie): Clean up this quick and dirty implementation
def generate_montecarlo(rl_agent: Agent, episodes: int = 10000):
    playdata = Kafka()
    random_agent = RandomAgent()
    for _ in tqdm(range(episodes), desc="Generating data"):
        _, episode_data = evaluate_game(agent1=random_agent, agent2=rl_agent)
        for x in range(1, len(episode_data), 2):
            assert episode_data[x].agent_id == 1
            if x == len(episode_data) - 1:
                # The RL agent made the last turn
                playdata.send(
                    process_playdata_json(
                        {
                            "initial_state": episode_data[x].state.text_board.flatten(),
                            "action": Board(
                                np_board=episode_data[x].action._board, agent_is_x=False
                            ).text_board.flatten(),
                            "resultant_state": episode_data[
                                x
                            ].resultant_state.text_board.flatten(),
                            "reward": episode_data[x].reward,
                            "agent_is_x": False,
                        }
                    )
                )
            else:
                # This is not the last turn
                playdata.send(
                    process_playdata_json(
                        {
                            "initial_state": episode_data[x].state.text_board.flatten(),
                            "action": Board(
                                np_board=episode_data[x].action._board, agent_is_x=False
                            ).text_board.flatten(),
                            "resultant_state": episode_data[
                                x + 1
                            ].resultant_state.text_board.flatten(),
                            "reward": episode_data[x].reward
                            - episode_data[x + 1].reward,
                            "agent_is_x": False,
                        }
                    )
                )


if __name__ == "__main__":
    agent_data = Path("../agent_data/agent_data.pickle")
    assert agent_data.exists()

    rl_agent = QLearningAgent(save_path=agent_data)
    generate_montecarlo(rl_agent=rl_agent)
