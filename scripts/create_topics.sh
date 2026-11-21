#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"
RAW="${KAFKA_TOPIC_RAW:-tweets_raw}"
ANALYZED="${KAFKA_TOPIC_ANALYZED:-tweets_analyzed}"

for TOPIC in "$RAW" "$ANALYZED"; do
  echo "→ Création topic $TOPIC"
  docker compose exec -T kafka kafka-topics.sh \
    --bootstrap-server kafka:9092 \
    --create --if-not-exists \
    --topic "$TOPIC" \
    --partitions 3 --replication-factor 1
done

docker compose exec -T kafka kafka-topics.sh --bootstrap-server kafka:9092 --list