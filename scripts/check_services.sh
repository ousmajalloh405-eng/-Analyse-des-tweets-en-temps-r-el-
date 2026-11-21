#!/usr/bin/env bash
set -uo pipefail

echo "== Vérification des services =="
docker compose ps || true

echo
echo "== Kafka : liste des topics =="
docker compose exec -T kafka kafka-topics.sh --bootstrap-server kafka:9092 --list || echo "Kafka KO"

echo
echo "== MongoDB : ping =="
docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" || echo "Mongo KO"

echo
echo "== Comptage documents (analyzed_tweets) =="
docker compose exec -T mongodb mongosh --quiet \
  --eval "db.getSiblingDB('${MONGO_DB:-tweets}').${MONGO_COLLECTION:-analyzed_tweets}.countDocuments()" || true

echo
echo "== Spark UI =="
curl -sf http://localhost:8080 >/dev/null && echo "Spark UI OK" || echo "Spark KO"

echo
echo "== Dashboard =="
curl -sf http://localhost:8501/_stcore/health >/dev/null && echo "Dashboard OK" || echo "Dashboard KO"