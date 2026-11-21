.PHONY: help up down logs test lint package topics

help:
	@echo "up       : démarre la stack Docker"
	@echo "down     : arrête la stack"
	@echo "logs     : suit les logs"
	@echo "topics   : crée les topics Kafka"
	@echo "test     : lance pytest"
	@echo "lint     : lance ruff"
	@echo "package  : génère dist/realtime-twitter-sentiment.zip"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

topics:
	bash scripts/create_topics.sh

test:
	pytest -q

lint:
	ruff check .

package:
	bash scripts/package.sh

	run-producer:
	python -m src.producer.run_producer

run-spark:
	python -m src.spark.stream_job