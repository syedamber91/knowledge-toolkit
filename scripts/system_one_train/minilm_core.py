"""Shared by training and the VPS server: MiniLM chunked mean-pool embedding.
all-MiniLM-L6-v2 truncates at 256 tokens, notes are ~1.8k tokens -> chunk, embed, mean-pool."""
import numpy as np

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_WORDS, MAX_CHUNKS = 180, 10


def embed_text(model, title, text):
    w = (title + ". " + text).split() or ["empty"]
    chunks = [" ".join(w[i:i + CHUNK_WORDS]) for i in range(0, len(w), CHUNK_WORDS)][:MAX_CHUNKS]
    v = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False).mean(0)
    return v / np.linalg.norm(v)
