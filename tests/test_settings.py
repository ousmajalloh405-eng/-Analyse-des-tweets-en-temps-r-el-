from config.settings import Settings


def test_defaults():
    s = Settings(_env_file=None)
    assert s.kafka_topic_raw == "tweets_raw"
    assert s.producer_mode in {"simulator", "twitter"}


def test_override(monkeypatch):
    monkeypatch.setenv("KAFKA_TOPIC_RAW", "custom_raw")
    s = Settings(_env_file=None)
    assert s.kafka_topic_raw == "custom_raw"