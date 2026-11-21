"""Client Twitter/X API v2 (Tweepy). Requiert TWITTER_BEARER_TOKEN."""
from __future__ import annotations

from typing import Iterator

import tweepy

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TwitterStreamError(RuntimeError):
    pass


def stream_tweets(bearer_token: str, keywords: str) -> Iterator[dict]:
    if not bearer_token:
        raise TwitterStreamError(
            "TWITTER_BEARER_TOKEN vide. Utilise PRODUCER_MODE=simulator "
            "ou renseigne un token valide (API X v2, accès payant/limité)."
        )

    rules = [t.strip() for t in keywords.split(",") if t.strip()]
    if not rules:
        raise TwitterStreamError("TWITTER_KEYWORDS est vide.")

    client = tweepy.Client(bearer_token=bearer_token)
    try:
        # Filtre simple : OR des mots-clés
        query = " OR ".join(rules)
        for tweet in tweepy.StreamingClient(bearer_token).filter(
            tweet_fields=["created_at", "lang", "author_id", "entities"],
            expansions=["author_id"],
            rule=query,
        ):
            if tweet.data:
                data = tweet.data
                hashtags = []
                entities = data.get("entities") or {}
                for tag in entities.get("hashtags", []):
                    hashtags.append(f"#{tag['tag']}")
                yield {
                    "id": str(data["id"]),
                    "text": data["text"],
                    "created_at": data.get("created_at", "").isoformat()
                    if data.get("created_at")
                    else "",
                    "author_id": str(data.get("author_id", "")),
                    "lang": data.get("lang", ""),
                    "hashtags": hashtags,
                    "source": "twitter",
                }
    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur API Twitter: %s", exc)
        raise TwitterStreamError(str(exc)) from exc