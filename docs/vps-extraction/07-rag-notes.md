# What RAG means here, and what Krish Naik's course adds (2026-11-05)

Source: Learning Vault AI hub, `wiki/personas/krish-naik/` (14 notes read by a Sonnet agent; each read only to ~900 characters of its synthesis text, so UNCHECKED beyond that). The agent's points, not course quotes.

**RAG, plain:** search your own files, pull out the few passages that match, label each with where it came from, hand them plus the question to the model, and make it answer only from them.

**Chunks:** course default is a recursive splitter (example 1000 chars, 100 overlap), chunks plus metadata (page, source, character count) go in a vector store. "Store as chunks" is implied, not a stated rule.

**Retrieval upgrades listed:** hybrid (BM25 + vectors), MMR, rerank, HyDE, query expansion, query decomposition, document grading, self-correcting loops.

**Gaps for our case:** nothing on tables or numbers; hallucination checks are LLM-judged, not mechanical; nothing on refusing when evidence is missing (its fallback is web search, which breaks our "only from files" rule); semantic chunking and whitespace cleaning would damage tables.

**Decision for BIOCON (proposal, owner to confirm):**
1. One page = one chunk. Our annual-report files are already one per page; filings: one page each. No sentence-based splitting.
2. Source of truth stays plain text in git (with source_url, date, page). The search index (FTS5 + vectors) is rebuilt from it and NOT committed.
3. Retrieve hybrid, then check every number mechanically against the retrieved page; no match = refuse.
4. Try query decomposition and rerank only if the golden set shows misses.
