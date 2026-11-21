"""Point d'entrée producteur : lit .env, choisit simulateur ou Twitter, publie dans Kafka."""
from __future__ import annotations

import json
import signal
import sys

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from config.settings import get_settings
from src.producer import simulator, twitter_client
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)
_running = True


def _handle_stop(signum, frame):  # noqa: ARG001
    global _running
    _running = False
    logger.info("Arrêt demandé, fermeture propre...")


def _build_producer(bootstrap: str, retries: int = 10) -> KafkaProducer:
    import time

    for attempt in range(1, retries + 1):
        try:
            return KafkaProducer(
                bootstrap_servers=bootstrap,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
                acks="all",
                retries=5,
                linger_ms=50,
            )
        except NoBrokersAvailable:
            logger.warning("Kafka indisponible (tentative %d/%d)", attempt, retries)
            time.sleep(3)
    raise RuntimeError("Kafka injoignable après plusieurs tentatives.")


def main() -> int:
    setup_logging()
    settings = get_settings()
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    producer = _build_producer(settings.kafka_bootstrap_servers)
    topic = settings.kafka_topic_raw
    logger.info("Producteur prêt → topic=%s mode=%s", topic, settings.producer_mode)

    if settings.producer_mode == "twitter":
        source = twitter_client.stream_tweets(
            settings.twitter_bearer_token or "", settings.twitter_keywords
        )
    else:
        source = simulator.stream_tweets(rate_per_sec=settings.simulator_rate_per_sec)

    sent = 0
    try:
        for tweet in source:
            if not _running:
                break
            producer.send(topic, tweet)
            sent += 1
            if sent % 50 == 0:
                logger.info("%d tweets publiés", sent)
    finally:
        producer.flush()
        producer.close()
        logger.info("Producteur arrêté. Total publié: %d", sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())