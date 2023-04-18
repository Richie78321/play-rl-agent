# Play RL Agent

A Tic-Tac-Toe RL agent that learns from human play over the internet.

## Running the Project

Make sure that you have Docker and Docker Compose V2 installed before proceeding. All commands below should be run from the root directory of the project.

### 1. Build the system images
```bash
docker compose build
```

### 2. Start the system
```bash
docker compose up -d
```

At this point, the system is running.

The frontend is available at `http://localhost/`.

The Agent REST API is available at `http://localhost/api/agent/`.

The Playdata REST API is available at `http://localhost/api/playdata`.

PGAdmin (for interacting with the Postgres database) is available at `http://localhost:8081/`.

### 3. Take down the system
```bash
docker compose down
```

### 4. Remove allocated resources
```bash
docker compose rm
```

## RL Agent Evaluation

To reproduce the RL agent performance evaluation, you must:
1. Create a Python virtual environment and install the requirements located in `api/requirements.txt`.
2. Install `jupyter` and `matplotlib` and run a Jupyter Notebook server by running `jupyter-notebook`.
3. Ensure the system running, such that the Postgres database is accessible from the host system on port `5432`.
4. Run the `api/agent-api/agent_performance.ipynb` Jupyter Notebook to evaluate the RL agent's performance when trained on the data available in the Postgres database.

## Components

### Agent REST API

Located in `api/agent-api/`.

This is a Flask REST API that the frontend uses to get the agent's moves for Tic-Tac-Toe.

### Playdata REST API

Located in `api/playdata-api/`.

This is a Flask REST API that the frontend uses to submit Tic-Tac-Toe game data for training.

### TicTacToe Library

Located in `api/tictactoe/`.

This is a library containing the core logic for the Tic-Tac-Toe RL agent. It is used by both the Agent and Playdata APIs.

### Frontend

Located in `frontend/`.

This is a Next.js (a React framework) frontend that is compiled to static HTML. It contains a simple Tic-Tac-Toe UI.

### Postgres

Configured in `postgres.sql`.

Postgres is used to store the recorded game data for training.

### Logstash

Configured in `logstash.conf`.

Logstash consumes game data from the Kafka topic and stores it in Postgres.

### Nginx

Configured in `nginx.conf`.

Nginx is used as a reverse proxy to expose the frontend, Agent API, and Playdata API over the same HTTP endpoint.
