"""Bookend context packing.

Models attend better to the start and end of a long context than to its middle
(lost-in-the-middle; Post 03). Bookend packing places the highest-ranked chunk
first and the second-highest last, filling weaker chunks into the middle, so the
most relevant evidence sits where the model reads it best.
"""
from __future__ import annotations


def bookend_pack(ranked_chunks: list[str]) -> list[str]:
    """Reorder chunks (already sorted best-first) so the two strongest bookend the rest."""
    if len(ranked_chunks) <= 2:
        return list(ranked_chunks)
    best, second, *rest = ranked_chunks
    return [best, *rest, second]
