from substack_toolkit.topics import keywords, match_topics


def test_match_topics_aliases_and_canonical():
    text = "We used dbt and Airflow to populate the data warehouse."
    topics = match_topics(text)
    assert "dbt" in topics
    assert "Apache Airflow" in topics
    assert "Data Warehouse" in topics


def test_match_topics_is_case_insensitive():
    assert "dbt" in match_topics("DBT is great")


def test_match_topics_whole_word_only():
    # "dbt" embedded inside another token must not match.
    assert "dbt" not in match_topics("the adbtx library")


def test_match_topics_dedupes_repeated_aliases():
    topics = match_topics("Spark spark PySpark everywhere")
    assert topics.count("Apache Spark") == 1


def test_match_topics_empty():
    assert match_topics("") == []


def test_keywords_returns_most_frequent_terms():
    text = "pipeline pipeline pipeline ingestion ingestion lineage"
    kw = keywords(text, limit=2)
    assert kw[0] == "pipeline"
    assert "ingestion" in kw
