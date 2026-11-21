"""Job Spark Structured Streaming : Kafka → NLP → MongoDB."""
from __future__ import annotations

import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType

from config.settings import get_settings
from src.spark.sentiment import analyze
from src.storage.mongo_writer import write_batch
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

SCHEMA = StructType(
    [
        StructField("id", StringType()),
        StructField("text", StringType()),
        StructField("created_at", StringType()),
        StructField("author_id", StringType()),
        StructField("lang", StringType()),
        StructField("hashtags", StringType()),
        StructField("source", StringType()),
    ]
)


def _analyze_row(row) -> dict:
    result = analyze(row["text"])
    return {
        "_id": row["id"],
        "tweet_id": row["id"],
        "text": row["text"],
        "cleaned_text": result.cleaned_text,
        "author_id": row["author_id"],
        "lang": row["lang"],
        "hashtags": row["hashtags"] or "",
        "source": row["source"],
        "created_at": row["created_at"],
        "polarity": float(result.polarity),
        "sentiment": result.label,
    }


def run_batch(batch_df, batch_id: int) -> None:
    rows = batch_df.collect()
    if not rows:
        logger.info("Batch %d vide", batch_id)
        return
    docs = [_analyze_row(r) for r in rows]
    inserted, skipped = write_batch(docs)
    logger.info("Batch %d : %d insérés, %d doublons ignorés", batch_id, inserted, skipped)


def main() -> int:
    setup_logging()
    settings = get_settings()

    spark = (
    SparkSession.builder.appName("tweets-sentiment")
    .master("local[*]")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    .getOrCreate()
)
    spark.sparkContext.setLogLevel("WARN")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.kafka_bootstrap_servers)
        .option("subscribe", settings.kafka_topic_raw)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false") # <-- Ajoute cette ligne
        .load()
    )

    parsed = raw.select(
        F.from_json(F.col("value").cast("string"), SCHEMA).alias("d")
    ).select("d.*").filter(F.col("id").isNotNull())

    query = (
        parsed.writeStream.foreachBatch(run_batch)
        .option("checkpointLocation", settings.checkpoint_dir)
        .trigger(processingTime="10 seconds")
        .start()
    )
    logger.info("Streaming démarré, checkpoint=%s", settings.checkpoint_dir)
    query.awaitTermination()
    return 0


if __name__ == "__main__":
    sys.exit(main())