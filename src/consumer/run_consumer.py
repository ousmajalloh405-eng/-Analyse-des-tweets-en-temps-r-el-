"""Consommateur de debug : affiche les messages du topic raw."""
from __future__ import annotations

import json
import signal
import sys

from kafka import KafkaConsumer

from config.settings import get_settings
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)
_running = True


def _stop(*_):
    global _running
    _running = False


def main() -> int:
    setup_logging()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    settings = get_settings()

    consumer = KafkaConsumer(
        settings.kafka_topic_raw,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="debug-consumer",
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    logger.info("Consumer attaché à %s", settings.kafka_topic_raw)
    count = 0
    try:
        for msg in consumer:
            if not _running:
                break
            count += 1
            logger.info("[%d] %s", count, msg.value.get("text", "")[:120])
    finally:
        consumer.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())