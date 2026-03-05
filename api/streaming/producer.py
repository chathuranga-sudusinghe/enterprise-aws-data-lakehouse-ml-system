from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "fraud-transactions")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

sample_transaction = {
    "TransactionID": 12345,
    "TransactionDT": 86400,
    "TransactionAmt": 150.0,
    "card1": 1000,
    "card2": 111,
    "card3": 150,
    "card4": "visa",
    "addr1": 325,
}

try:
    future = producer.send(TOPIC, sample_transaction)
    record_md = future.get(timeout=10)
    producer.flush()
    print(f"Sent to Kafka: topic={record_md.topic}, partition={record_md.partition}, offset={record_md.offset}")
finally:
    producer.close()