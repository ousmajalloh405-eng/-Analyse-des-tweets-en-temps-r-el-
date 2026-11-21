from itertools import islice

from src.producer.simulator import stream_tweets


def test_stream_yields_expected_schema():
    tweets = list(islice(stream_tweets(rate_per_sec=1000, seed=1), 5))
    assert len(tweets) == 5
    for t in tweets:
        assert set(t) == {
            "id", "text", "created_at", "author_id",
            "lang", "hashtags", "source",
        }
        assert t["source"] == "simulator"
        assert isinstance(t["hashtags"], list)


def test_simulator_is_deterministic_with_seed():
    a = list(islice(stream_tweets(rate_per_sec=1000, seed=7), 3))
    b = list(islice(stream_tweets(rate_per_sec=1000, seed=7), 3))
    assert [t["text"] for t in a] == [t["text"] for t in b]