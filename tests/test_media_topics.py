from media_core.topics import TOPIC_VOCABULARY, keywords, match_topics


def test_extended_vocabulary_includes_base_and_systemdesign():
    # base (data-engineering) topic still present
    assert "dbt" in TOPIC_VOCABULARY
    # extended (system-design / AI) topics added
    for t in ("Kubernetes", "System Design", "LLM", "Caching"):
        assert t in TOPIC_VOCABULARY


def test_match_topics_finds_both_layers():
    text = ("This video covers kubernetes and microservices, plus how to use "
            "kafka for streaming and dbt for the warehouse.")
    topics = match_topics(text)
    assert "Kubernetes" in topics
    assert "Microservices" in topics
    assert "Apache Kafka" in topics
    assert "dbt" in topics


def test_match_topics_avoids_bare_rest_false_positive():
    # "rest" as a plain word must NOT trigger the REST topic (alias is "rest api").
    assert "REST" not in match_topics("take a rest and relax")
    assert "REST" in match_topics("we expose a REST API for clients")


def test_keywords_reused():
    assert isinstance(keywords("kafka streaming kafka pipelines"), list)
