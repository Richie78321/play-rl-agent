from flask import Flask, jsonify, request
from flask_cors import CORS
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from playdatakafka import Kafka
from tictactoe.schema import state_schema
from tictactoe.states import Board
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app)

# Configuration required to use Flask behind a proxy.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

kafka = Kafka()

playdata_validator = Draft7Validator(
    schema={
        "type": "object",
        "properties": {
            "initial_state": state_schema,
            "action": state_schema,
            "resultant_state": state_schema,
            "reward": {"type": "number"},
            "agent_is_x": {"type": "boolean"},
        },
        "required": ["initial_state", "action", "resultant_state", "reward"],
        "additional_properties": False,
    }
)


def process_playdata_json(playdata_json):
    initial_state = Board.from_text_board(
        playdata_json["initial_state"], agent_is_x=playdata_json["agent_is_x"]
    )
    action = Board.from_text_board(
        playdata_json["action"], agent_is_x=playdata_json["agent_is_x"]
    )
    normalization_transform, _ = initial_state.normalization_transform
    # Normalize the initial state, and apply the same transform to the action
    # so it does not lose its meaning.
    initial_state = initial_state.transform(normalization_transform)
    action = action.transform(normalization_transform)

    resultant_state = Board.from_text_board(
        playdata_json["resultant_state"], agent_is_x=playdata_json["agent_is_x"]
    )
    normalization_transform, _ = resultant_state.normalization_transform
    resultant_state = resultant_state.transform(normalization_transform)

    return {
        "initial_state": initial_state.code,
        "action": action.code,
        "resultant_state": resultant_state.code,
        "reward": playdata_json["reward"],
    }


@app.post("/submit")
def submit_playdata():
    # Validate that the JSON playdata matches the required schema before
    # processing it.
    playdata = request.get_json()
    try:
        playdata_validator.validate(playdata)
    except ValidationError as e:
        return jsonify({"message": str(e)}), 400

    kafka.send(process_playdata_json(playdata))
    return jsonify({"message": "success"}), 200
