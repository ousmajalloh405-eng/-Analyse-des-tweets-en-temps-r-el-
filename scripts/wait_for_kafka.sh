#!/usr/bin/env bash
set -euo pipefail

RETRIES=${RETRIES:-30}
echo "Attente de Kafka..."
for i in $(seq 1 "$RETRIES"); do
  if docker compose exec -T kafka kafka-topics.sh --bootstrap-server kafka:9092 --list >/dev/null 2>&1; then
    echo "Kafka prêt."
    exit 0
  fi
  sleep 2
done
echo "Kafka indisponible." >&2
exit 1