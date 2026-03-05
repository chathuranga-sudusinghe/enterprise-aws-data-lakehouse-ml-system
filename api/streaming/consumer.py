# ------------------------------------------------------------
# Kafka Streaming Consumer
#
# This service:
# 1. Connects to Kafka broker
# 2. Listens for new fraud transaction events
# 3. Sends transactions to the FastAPI prediction API
# 4. Logs prediction results
#
# Architecture flow:
# Producer → Kafka Topic → Consumer → FastAPI Model → Prediction
# ------------------------------------------------------------

from kafka import KafkaConsumer, KafkaAdminClient
import json
import logging
import os
import time
import requests


# ------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Environment configuration
# Values come from docker-compose environment variables
# ------------------------------------------------------------

# Kafka topic name
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "fraud-transactions")

# Kafka broker address
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

# FastAPI prediction endpoint
API_URL = os.getenv("API_URL", "http://api:8000/predict")

# Kafka consumer group ID
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "fraud-consumer-v1")


logger.info(f"Connecting to Kafka broker at {KAFKA_SERVER}")
logger.info(f"Will call prediction API at {API_URL}")


# ------------------------------------------------------------
# Retry helper for API requests
# Ensures transient API failures don't break the stream
# ------------------------------------------------------------
def post_with_retry(url, payload, retries=30, sleep=2):

    last_err = None

    for attempt in range(1, retries + 1):

        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            return r.json()

        except Exception as e:
            last_err = e
            logger.warning(f"Retrying API call (attempt {attempt}/{retries})... {e}")
            time.sleep(sleep)

    raise last_err


# ------------------------------------------------------------
# Wait for Kafka broker to become available
# Prevents consumer from crashing during startup
# ------------------------------------------------------------
def wait_for_kafka(bootstrap: str, timeout_s: int = 120) -> None:

    start = time.time()

    while True:

        try:
            admin = KafkaAdminClient(
                bootstrap_servers=bootstrap,
                request_timeout_ms=5000,
            )

            admin.close()
            logger.info("Kafka is reachable.")
            return

        except Exception as e:

            if time.time() - start > timeout_s:
                logger.exception("Kafka did not become ready in time.")
                raise

            logger.info(f"Waiting for Kafka... ({e})")
            time.sleep(2)


# Wait until Kafka is ready before starting consumer
wait_for_kafka(KAFKA_SERVER, timeout_s=120)


# ------------------------------------------------------------
# Kafka Consumer initialization
# ------------------------------------------------------------

consumer = KafkaConsumer(

    # Topic to subscribe
    KAFKA_TOPIC,

    # Kafka broker address
    bootstrap_servers=KAFKA_SERVER,

    # Deserialize message JSON
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),

    # Start reading from earliest offset
    auto_offset_reset="earliest",

    # Enable automatic offset commit
    enable_auto_commit=True,

    # Consumer group ID
    group_id=KAFKA_GROUP_ID
)

logger.info("Kafka consumer started...")


# ------------------------------------------------------------
# Main streaming loop
# ------------------------------------------------------------

for message in consumer:

    try:
        # Extract transaction payload
        transaction = message.value

        if transaction is None:
            logger.warning("Skipping empty Kafka message")
            continue

    except Exception as e:
        logger.warning(f"Skipping invalid Kafka message: {e}")
        continue


    logger.info(f"Received transaction: {transaction}")

    try:
        # Send transaction to ML prediction API
        result = post_with_retry(API_URL, {"data": transaction})

        logger.info(f"Prediction result: {result}")

    except Exception:
        logger.exception("Error calling prediction API")