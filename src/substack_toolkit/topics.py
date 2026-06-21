"""Canonical topic vocabulary and lexical matchers.

This module is the cross-channel linking seam: every channel matches its posts
against the SAME canonical vocabulary, so identical topics (e.g. "dbt") collapse
to one shared Obsidian topic note regardless of which publication they came from.

Extend ``TOPIC_VOCABULARY`` to recognise more topics; re-running the vault build
re-links every post against the updated vocabulary.
"""

from __future__ import annotations

import re
from collections import Counter

# Canonical topic name -> alias phrases (matched case-insensitively, whole-word).
TOPIC_VOCABULARY: dict[str, list[str]] = {
    "Data Engineering": ["data engineering"],
    "dbt": ["dbt", "data build tool"],
    "Apache Airflow": ["airflow"],
    "Apache Kafka": ["kafka"],
    "Apache Spark": ["spark", "pyspark"],
    "Apache Iceberg": ["iceberg"],
    "Apache Flink": ["flink"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "Delta Lake": ["delta lake"],
    "BigQuery": ["bigquery"],
    "Data Modeling": ["data modeling", "data modelling", "dimensional model"],
    "Data Warehouse": ["data warehouse"],
    "Data Lake": ["data lake"],
    "Lakehouse": ["lakehouse"],
    "Orchestration": ["orchestration"],
    "Streaming": ["streaming", "stream processing"],
    "Batch Processing": ["batch processing"],
    "Change Data Capture": ["change data capture", "cdc"],
    "Data Quality": ["data quality"],
    "Data Governance": ["data governance"],
    "ETL": ["etl", "elt"],
}

# Precompiled whole-word, case-insensitive patterns per alias.
_COMPILED: dict[str, list[re.Pattern]] = {
    canon: [re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
            for alias in aliases]
    for canon, aliases in TOPIC_VOCABULARY.items()
}

_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are",
    "was", "but", "not", "all", "can", "has", "have", "will", "what", "how",
    "why", "when", "which", "into", "out", "about", "their", "them", "its",
    "our", "more", "less", "than", "then", "also", "such", "may", "one", "two",
    "use", "using", "used", "based", "part", "post", "article", "data",
}
_WORD_RE = re.compile(r"[a-z][a-z0-9]{3,}")


def match_topics(text: str) -> list[str]:
    """Return canonical topics found in ``text`` (deduped, vocabulary order)."""
    if not text:
        return []
    found: list[str] = []
    for canon, patterns in _COMPILED.items():
        if any(p.search(text) for p in patterns):
            found.append(canon)
    return found


def keywords(text: str, limit: int = 6) -> list[str]:
    """Return the most frequent non-stopword terms in ``text`` (secondary tags)."""
    if not text:
        return []
    words = [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS]
    return [w for w, _ in Counter(words).most_common(limit)]
