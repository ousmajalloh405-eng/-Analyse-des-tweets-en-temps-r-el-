"""Écriture idempotente dans MongoDB."""
from __future__ import annotations

from typing import Iterable

from pymongo import MongoClient
from pymongo.errors import BulkWriteError, PyMongoError

from config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
_client: MongoClient | None = None


def _get_collection():
    global _client
    settings = get_settings()
    if _client is None:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
    return _client[settings.mongo_db][settings.mongo_collection]


def write_batch(docs: Iterable[dict]) -> tuple[int, int]:
    docs = list(docs)
    if not docs:
        return 0, 0
    coll = _get_collection()
    try:
        coll.insert_many(docs, ordered=False)
        return len(docs), 0
    except BulkWriteError as bwe:
        write_errors = bwe.details.get("writeErrors", [])
        dup = sum(1 for e in write_errors if e.get("code") == 11000)
        other = len(write_errors) - dup
        inserted = len(docs) - len(write_errors)
        if other:
            logger.error("%d erreurs d'écriture non-duplicat", other)
        return inserted, dup
    except PyMongoError as exc:
        logger.error("Erreur Mongo: %s", exc)
        return 0, 0