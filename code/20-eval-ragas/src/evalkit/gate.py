"""The regression gate.

An eval only protects you if a drop blocks the deploy (Post 20). This gate compares
a run's metrics against a saved baseline and fails if any metric falls more than a
tolerance below it. The default 5% tolerance is a starting point, not a law — set it
per metric to what your traffic can absorb.
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_TOLERANCE = 0.05  # 5% absolute drop, configurable


@dataclass(frozen=True)
class GateResult:
    passed: bool
    regressions: dict  # metric -> (baseline, current)


def check_regression(
    current: dict[str, float],
    baseline: dict[str, float],
    tolerance: float = DEFAULT_TOLERANCE,
) -> GateResult:
    """Fail if any baseline metric drops by more than ``tolerance`` (absolute) in ``current``.

    Metrics present in the baseline but missing from ``current`` count as a regression.
    New metrics not in the baseline are ignored.
    """
    regressions: dict = {}
    for name, base in baseline.items():
        cur = current.get(name)
        if cur is None or cur < base - tolerance:
            regressions[name] = (base, cur)
    return GateResult(passed=not regressions, regressions=regressions)
