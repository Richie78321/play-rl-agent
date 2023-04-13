import os
import threading
import time
from pathlib import Path
from typing import Tuple

import psycopg2
import schedule
from readerwriterlock import rwlock

from tictactoe.agent import QLearningAgent


# https://schedule.readthedocs.io/en/stable/background-execution.html
class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)


continuous_thread = ScheduleThread()
continuous_thread.start()

TRAINING_CRON_FREQUENCY_SECS = 10


class LearningAgentWrapper:
    def __init__(self):
        agent_data_path_str = os.getenv("AGENT_DATA_PATH")
        if agent_data_path_str is None:
            agent_data_path_str = "../../agent_data/agent_data.pickle"

        self.agent_data_path = Path(agent_data_path_str)
        self.agent = QLearningAgent(self.agent_data_path)

        # RWLock has writer priority to avoid writer starvation from incoming requests.
        my_rwlock = rwlock.RWLockWrite()
        self.agent_write_lock = my_rwlock.gen_wlock()
        self.agent_read_lock = my_rwlock.gen_rlock()

        if os.environ.get("TRAINING_DISABLE") is None or not bool(
            os.environ.get("TRAINING_DISABLE")
        ):
            self._playdata = PostgresPlaydata(os.environ.get("POSTGRES_CONNECTION"))
            # Schedule the training CRON
            schedule.every(TRAINING_CRON_FREQUENCY_SECS).seconds.do(self._training_cron)
            print("Training CRON set.")
        else:
            print("Training disabled.")

    def _training_cron(self):
        with self.agent_read_lock:
            # Save the current agent to disk.
            self.agent.save()

            # Make a clone of the agent from disk.
            new_agent = QLearningAgent(self.agent_data_path)
            new_agent.load()

        # TODO(richie): Implement some strategy for pruning old data. For now
        # data is only used once.
        training_data = self._playdata.get()
        print(f"Training with {len(training_data)} data points")
        if len(training_data) <= 0:
            return

        new_agent.train(data=training_data)

        with self.agent_write_lock:
            # Only hold the write lock to swap for the new agent and save to disk.
            self.agent = new_agent
            self.agent.save()

        print("Training completed")


class PostgresPlaydata:
    def __init__(self, conn_str):
        self._connection = psycopg2.connect(conn_str)

    def get(self) -> Tuple[int, int, int, float]:
        # For now data is fully loaded into memory. In the future this could be improved
        # if necessary.
        with self._connection.cursor() as cur:
            cur.execute(
                "SELECT initial_state, action, resultant_state, reward FROM playdata"
            )
            values = cur.fetchall()

            # Delete the values that are being used for training.
            cur.execute("DELETE FROM playdata")
            self._connection.commit()

        return values
