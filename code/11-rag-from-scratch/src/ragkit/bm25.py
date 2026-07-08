"""A minimal, dependency-free BM25 lexical index.

BM25 scores a document against a query by summing, over the query terms, an IDF
weight times a saturating term-frequency factor that is normalised by document
length. It is the classical strong baseline for keyword retrieval and the lexical
half of hybrid search (see Post 09). This implementation is intentionally small
and pure-Python so it runs and tests offline.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_WORD = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs = docs
        self.doc_tokens = [tokenize(d) for d in docs]
        self.doc_len = [len(t) for t in self.doc_tokens]
        self.avgdl = (sum(self.doc_len) / len(docs)) if docs else 0.0
        self.tf = [Counter(t) for t in self.doc_tokens]
        # document frequency per term
        df: Counter[str] = Counter()
        for toks in self.doc_tokens:
            for term in set(toks):
                df[term] += 1
        n = len(docs)
        # BM25 idf with the +1 smoothing that keeps weights non-negative
        self.idf = {
            term: math.log(1 + (n - d + 0.5) / (d + 0.5)) for term, d in df.items()
        }

    def score(self, query: str, index: int) -> float:
        score = 0.0
        dl = self.doc_len[index]
        tf = self.tf[index]
        for term in tokenize(query):
            if term not in self.idf or tf[term] == 0:
                continue
            freq = tf[term]
            denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
            score += self.idf[term] * (freq * (self.k1 + 1)) / denom
        return score

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """Return ``(doc_index, score)`` for the top-k documents, best first."""
        ranked = sorted(
            ((i, self.score(query, i)) for i in range(len(self.docs))),
            key=lambda x: x[1],
            reverse=True,
        )
        return [(i, s) for i, s in ranked[:top_k] if s > 0]
