"""Configuration centralisée, chargée depuis l'environnement."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Kafka
    kafka_bootstrap_servers: str = Field("localhost:9092")
    kafka_topic_raw: str = Field("tweets_raw")
    kafka_topic_analyzed: str = Field("tweets_analyzed")

    # Mongo
    mongo_uri: str = Field("mongodb://admin:changeme@localhost:27017/?authSource=admin")
    mongo_db: str = Field("tweets")
    mongo_collection: str = Field("analyzed_tweets")

    # Twitter (optionnel)
    twitter_bearer_token: str | None = None
    twitter_keywords: str = Field("data,engineering,spark")

    # Producer
    producer_mode: Literal["simulator", "twitter"] = "simulator"
    simulator_rate_per_sec: int = 5

    # Spark
    spark_master: str = Field("local[*]")
    checkpoint_dir: str = Field("/tmp/spark-checkpoints")


def get_settings() -> Settings:
    return Settings()