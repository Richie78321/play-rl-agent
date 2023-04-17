import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from tictactoe.agent import QLearningAgent
from tictactoe.schema import state_schema
from tictactoe.states import Board
from training import LearningAgentWrapper
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app)

# Configuration required to use Flask behind a proxy.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

game_state_validator = Draft7Validator(
    schema={
        "type": "object",
        "properties": {
            "state": state_schema,
            "agent_is_x": {"type": "boolean"},
        },
        "required": ["state"],
        "additional_properties": False,
    }
)

agent_wrapper = LearningAgentWrapper()


def get_agent_action(game_state) -> Board:
    game_board = Board.from_text_board(
        game_state["state"], agent_is_x=game_state["agent_is_x"]
    )
    with agent_wrapper.agent_read_lock:
        action = agent_wrapper.agent.act(game_board)

    if not game_state["agent_is_x"]:
        # Swap back the symbols of the action if the agent is
        # not X.
        # TODO(richie): This should be refactored so it's not
        # a concern of the API.
        action = action.swap_symbols()

    return action


@app.post("/action")
def take_action():
    game_state = request.get_json()
    try:
        game_state_validator.validate(game_state)
    except ValidationError as e:
        return jsonify({"message": str(e)}), 400

    action = get_agent_action(game_state)
    return jsonify(
        {
            "message": "success",
            "action": list(action.text_board.flatten()),
        }
    )
