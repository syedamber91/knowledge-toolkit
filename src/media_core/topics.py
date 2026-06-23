"""Topic vocabulary for media capture.

Reuses the canonical data-engineering vocabulary from ``substack_toolkit`` so the
same topic name resolves identically everywhere, and EXTENDS it with the broader
software / system-design / AI terms common in YouTube and web content. The
keyword extractor is reused verbatim.
"""

from __future__ import annotations

import re

from substack_toolkit.topics import TOPIC_VOCABULARY as _BASE_VOCAB
from substack_toolkit.topics import keywords  # noqa: F401 (re-exported)

# Broader tech topics layered on top of the data-engineering base. Aliases are
# matched whole-word, case-insensitively; keep them specific enough to avoid
# false hits (e.g. "rest api"/"restful", not the bare word "rest").
_EXTRA_VOCABULARY: dict[str, list[str]] = {
    "System Design": ["system design"],
    "Distributed Systems": ["distributed system", "distributed systems",
                             "consensus", "raft", "paxos"],
    "Scalability": ["scalability", "scalable", "horizontal scaling",
                    "vertical scaling"],
    "Microservices": ["microservice", "microservices"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Docker": ["docker", "containerization", "containers"],
    "API Design": ["api design", "api gateway"],
    "REST": ["rest api", "restful"],
    "GraphQL": ["graphql"],
    "gRPC": ["grpc"],
    "Caching": ["caching", "cache", "redis", "memcached"],
    "Load Balancing": ["load balancing", "load balancer"],
    "Message Queue": ["message queue", "rabbitmq", "amazon sqs"],
    "Databases": ["postgresql", "postgres", "mysql", "relational database"],
    "NoSQL": ["nosql", "mongodb", "cassandra", "dynamodb"],
    "Networking": ["tcp/ip", "load balancing", "dns", "http/2", "http/3"],
    "Observability": ["observability", "prometheus", "grafana",
                      "distributed tracing"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "Infrastructure as Code": ["infrastructure as code", "terraform"],
    "Cloud": ["aws", "azure", "google cloud", "gcp"],
    "Authentication": ["authentication", "oauth", "oauth2", "jwt", "openid"],
    "Security": ["encryption", "tls", "cybersecurity"],
    "Machine Learning": ["machine learning", "deep learning", "neural network"],
    "LLM": ["large language model", "llm", "gpt", "transformer model"],
    "RAG": ["retrieval augmented generation", "retrieval-augmented"],
    "MCP": ["model context protocol", "mcp"],
    "Web Development": ["web development", "frontend", "backend"],
    "Python": ["python"],
    # Education & productivity (common in YouTube / learning channels)
    "Learning": ["learning", "study", "studying", "how to learn",
                 "active recall", "spaced repetition", "flashcard",
                 "comprehension", "retention", "memorization"],
    "Productivity": ["productivity", "time management", "deep work",
                     "focus", "procrastination", "habit", "pomodoro"],
    "Career": ["career", "job search", "interview", "salary", "networking",
               "resume", "linkedin", "job offer", "internship"],
    "Education": ["education", "college", "university", "student",
                  "course", "degree", "class", "lecture", "exam",
                  "test-taking", "note-taking"],
    "AI & Future of Work": ["ai replacing", "automation replacing",
                             "future of work", "ai and jobs"],
}

# Merge: base first (preserves canonical ordering), then extras.
TOPIC_VOCABULARY: dict[str, list[str]] = {**_BASE_VOCAB, **_EXTRA_VOCABULARY}

_COMPILED: dict[str, list[re.Pattern]] = {
    canon: [re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
            for alias in aliases]
    for canon, aliases in TOPIC_VOCABULARY.items()
}


def match_topics(text: str) -> list[str]:
    """Return canonical topics found in ``text`` (deduped, vocabulary order)."""
    if not text:
        return []
    found: list[str] = []
    for canon, patterns in _COMPILED.items():
        if any(p.search(text) for p in patterns):
            found.append(canon)
    return found
