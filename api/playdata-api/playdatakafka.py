import json
import os

from kafka import KafkaProducer

KAFKA_PLAYDATA_TOPIC = "playdata"
kafka_enabled = os.environ.get("KAFKA_DISABLE") is None or not bool(
    os.environ.get("KAFKA_DISABLE")
)


class Kafka:
    def __init__(self):
        if kafka_enabled:
            if os.environ.get("KAFKA_BOOTSTRAP_SERVER") is None:
                raise EnvironmentError("Must define KAFKA_BOOTSTRAP_SERVER")
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVER")
            )

    def send(self, playdata):
        payload = json.dumps(playdata)
        if not kafka_enabled:
            print("Would have sent:", payload)
            return

        self._kafka_producer.send(
            topic=KAFKA_PLAYDATA_TOPIC,
            value=payload.encode(),
        )
