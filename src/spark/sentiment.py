"""Analyse de sentiment : nettoyage + scoring (TextBlob + fallback FR)."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from textblob import TextBlob

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
NON_WORD_RE = re.compile(r"[^a-zA-ZÀ-ÿ0-9#\s]")

# Lexique minimal français (extensible). Poids entre -1 et +1.
POSITIVE_FR = {
    "génial": 0.8, "genial": 0.8, "super": 0.7, "excellent": 0.9,
    "adore": 0.8, "aime": 0.6, "rapide": 0.5, "incroyable": 0.8,
    "parfait": 0.8, "bon": 0.4, "bien": 0.3, "top": 0.6,
    "cool": 0.5, "formidable": 0.9, "réussi": 0.7,
}
NEGATIVE_FR = {
    "nul": -0.8, "nulle": -0.8, "décevant": -0.7, "decevant": -0.7,
    "décevante": -0.7, "mauvais": -0.7, "lent": -0.5, "horrible": -0.9,
    "déteste": -0.8, "deteste": -0.8, "problème": -0.4, "probleme": -0.4,
    "bug": -0.4, "erreur": -0.4, "catastrophe": -0.9,
}


@dataclass
class SentimentResult:
    polarity: float
    label: str
    cleaned_text: str

    def to_dict(self) -> dict:
        return asdict(self)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = NON_WORD_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _lexicon_score(cleaned: str) -> tuple[float, int]:
    """Retourne (score moyen, nb de mots reconnus) via lexique FR."""
    tokens = cleaned.lower().split()
    scores = []
    for tok in tokens:
        if tok in POSITIVE_FR:
            scores.append(POSITIVE_FR[tok])
        elif tok in NEGATIVE_FR:
            scores.append(NEGATIVE_FR[tok])
    if not scores:
        return 0.0, 0
    return sum(scores) / len(scores), len(scores)


def _label(polarity: float, neutral_band: float = 0.05) -> str:
    if polarity > neutral_band:
        return "positive"
    if polarity < -neutral_band:
        return "negative"
    return "neutral"


def analyze(text: str) -> SentimentResult:
    cleaned = clean_text(text)

    # 1) Priorité au lexique FR si des mots sont reconnus
    fr_score, fr_hits = _lexicon_score(cleaned)
    if fr_hits > 0:
        return SentimentResult(
            polarity=fr_score, label=_label(fr_score), cleaned_text=cleaned
        )

    # 2) Sinon fallback TextBlob (anglais)
    try:
        polarity = TextBlob(cleaned).sentiment.polarity
    except Exception:  # noqa: BLE001
        polarity = 0.0
    return SentimentResult(polarity=polarity, label=_label(polarity), cleaned_text=cleaned)