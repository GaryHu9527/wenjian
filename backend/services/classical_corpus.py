from __future__ import annotations

import json
from pathlib import Path
from utils.cache import MemoryCache


class PoetryProvider:
    """Stable contract for a future Poetry API adapter; no external Go service is required now."""
    def search(self, query): raise NotImplementedError
    def get_author(self, name): raise NotImplementedError
    def get_poem(self, title): raise NotImplementedError


class ClassicalCorpusProvider(PoetryProvider):
    def __init__(self, cache_ttl_seconds=1800):
        seed = Path(__file__).resolve().parent.parent / "data" / "corpus_seed.json"
        self.items = json.loads(seed.read_text(encoding="utf-8"))
        self.cache = MemoryCache(cache_ttl_seconds)

    def search(self, query, keywords=None):
        query = (query or "").strip()
        words = [query, *((keywords or []))]
        key = "|".join(words)
        cached = self.cache.get(key)
        if cached is not None: return cached
        scored = []
        for item in self.items:
            haystack = " ".join(item.values())
            score = sum(len(word) if word and word in haystack else 0 for word in words)
            if score: scored.append((score, item))
        return self.cache.set(key, [item for _, item in sorted(scored, key=lambda entry: entry[0], reverse=True)[:10]])

    def get_author(self, name): return [item for item in self.items if item["author"] == name]
    def get_poem(self, title): return next((item for item in self.items if item["title"] == title), None)


def search_classical_text(query, keywords=None, provider=None):
    return (provider or ClassicalCorpusProvider()).search(query, keywords)
