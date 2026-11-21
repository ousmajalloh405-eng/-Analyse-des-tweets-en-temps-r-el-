from src.spark.sentiment import analyze, clean_text


def test_clean_text_removes_urls_and_mentions():
    cleaned = clean_text("Salut @bob regarde https://x.com #data")
    assert "http" not in cleaned
    assert "@bob" not in cleaned
    assert "#data" in cleaned


def test_positive():
    r = analyze("Spark est vraiment génial, j'adore !")
    assert r.label == "positive"
    assert r.polarity > 0


def test_negative():
    r = analyze("Cette expérience est nulle et décevante.")
    assert r.label == "negative"
    assert r.polarity < 0


def test_empty():
    r = analyze("")
    assert r.label == "neutral"
    assert r.polarity == 0.0