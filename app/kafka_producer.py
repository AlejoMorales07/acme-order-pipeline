from kafka import KafkaProducer
import json
import logging
from kafka.errors import NoBrokersAvailable
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MAX_RETRIES = 10
RETRY_DELAY = 5  # segundos

for attempt in range(1, MAX_RETRIES + 1):
    try:
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        logging.info("Conexión a Kafka exitosa (producer).")
        break
    except NoBrokersAvailable as e:
        logging.warning(f"Intento {attempt}: Kafka no disponible, reintentando en {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
else:
    logging.error("No se pudo conectar a Kafka después de varios intentos. Abortando producer.")
    exit(1)

def publish_order_event(order):
    producer.send("orders", order)
    producer.flush()