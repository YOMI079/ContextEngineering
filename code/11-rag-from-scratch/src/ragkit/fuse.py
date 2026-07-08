"""Reciprocal Rank Fusion (RRF).

RRF merges several ranked lists into one without needing their scores to be on the
same scale: each item gets ``sum(1 / (k + rank))`` over the lists it appears in,
where ``rank`` is 1-based. It is the parameter-light default for combining a dense
(vector) ranking with a lexical (BM25) ranking in hybrid search (Cormack et al.,
2009; see Post 09).
"""
from __future__ import annotations

from collections import defaultdict


def rrf(rankings: list[list], k: int = 60) -> list[tuple]:
    """Fuse ranked lists of item ids into one ranking.

    ``rankings`` is a list of lists; each inner list is item ids ordered best-first.
    Returns ``(item_id, fused_score)`` pairs, best first. Ties break by first
    appearance for determinism.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    scores: dict = defaultdict(float)
    first_seen: dict = {}
    order = 0
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
            if item not in first_seen:
                first_seen[item] = order
                order += 1
    return sorted(scores.items(), key=lambda kv: (-kv[1], first_seen[kv[0]]))
