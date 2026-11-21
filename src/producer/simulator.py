"""Générateur de tweets simulés pour le mode démo."""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Iterator

HASHTAGS = ["#data", "#spark", "#kafka", "#python", "#nlp", "#bigdata", "#streaming"]
SUBJECTS = ["Spark", "Kafka", "Python", "MongoDB", "Streamlit", "TextBlob"]
ADJECTIVES = ["génial", "nul", "correct", "incroyable", "décevant", "rapide", "lent"]
TEMPLATES = [
    "Je teste {subject}, c'est {adj} !",
    "{subject} en prod, franchement {adj}.",
    "Retour d'expérience sur {subject} : {adj}.",
    "Quelqu'un a un avis sur {subject} ? Perso {adj}.",
]


def _random_tweet(rng: random.Random) -> dict:
    template = rng.choice(TEMPLATES)
    text = template.format(
        subject=rng.choice(SUBJECTS), adj=rng.choice(ADJECTIVES)
    )
    hashtags = rng.sample(HASHTAGS, k=rng.randint(1, 3))
    return {
        "id": str(uuid.uuid4()),
        "text": f"{text} {' '.join(hashtags)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "author_id": f"user_{rng.randint(1000, 9999)}",
        "lang": "fr",
        "hashtags": hashtags,
        "source": "simulator",
    }


def stream_tweets(rate_per_sec: int = 5, seed: int = 42) -> Iterator[dict]:
    """Itère indéfiniment en produisant `rate_per_sec` tweets par seconde (approx.)."""
    import time

    rng = random.Random(seed)
    interval = 1.0 / max(rate_per_sec, 1)
    while True:
        yield _random_tweet(rng)
        time.sleep(interval)