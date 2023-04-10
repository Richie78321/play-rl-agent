import os

from flask import Flask, jsonify, request
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from kafka import KafkaProducer
from werkzeug.middleware.proxy_fix import ProxyFix

KAFKA_PLAYDATA_TOPIC = "playdata"

app = Flask(__name__)

# Configuration required to use Flask behind a proxy.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

playdata_validator = Draft7Validator(
    schema={
        "type": "object",
        "properties": {
            "initial_state": {"type": "string"},
            "action": {"type": "string"},
            "resultant_state": {"type": "string"},
            "reward": {"type": "number"},
        },
        "required": ["initial_state", "action", "resultant_state", "reward"],
        "additional_properties": False,
    }
)

if os.environ.get("KAFKA_BOOTSTRAP_SERVER") is None:
    raise EnvironmentError("Must define KAFKA_BOOTSTRAP_SERVER")
kafka_producer = KafkaProducer(
    bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVER")
)


@app.post("/submit")
def submit_playdata():
    # Validate that the JSON playdata matches the required schema before
    # sending it over Kafka.
    playdata = request.get_json()
    try:
        playdata_validator.validate(playdata)
    except ValidationError as e:
        return jsonify({"message": str(e)}), 400

    kafka_producer.send(topic=KAFKA_PLAYDATA_TOPIC, value=request.get_data())

    return jsonify({"message": "success"}), 200
