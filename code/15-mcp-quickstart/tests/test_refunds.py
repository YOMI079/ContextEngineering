"""Offline tests for the pure refund logic. stdlib + pytest; the MCP runtime is not needed."""
from __future__ import annotations

import pytest

from mcp_quickstart.refunds import Order, check_refund_eligibility


def test_simple_refund_is_eligible():
    d = check_refund_eligibility(Order("A1", total_usd=200, days_since_purchase=5), 50)
    assert d.eligible and not d.requires_manager_approval


def test_already_refunded_is_rejected():
    d = check_refund_eligibility(
        Order("A1", 200, 5, already_refunded=True), 50
    )
    assert not d.eligible and "already" in d.reason.lower()


def test_outside_window_is_rejected():
    d = check_refund_eligibility(Order("A1", 200, days_since_purchase=45), 50)
    assert not d.eligible and "window" in d.reason.lower()


def test_amount_over_total_is_rejected():
    d = check_refund_eligibility(Order("A1", total_usd=40, days_since_purchase=5), 50)
    assert not d.eligible and "exceeds" in d.reason.lower()


def test_large_refund_needs_manager_approval():
    d = check_refund_eligibility(Order("A1", total_usd=5000, days_since_purchase=5), 1500)
    assert d.eligible and d.requires_manager_approval


@pytest.mark.parametrize("amount", [0, -10])
def test_non_positive_amount_is_rejected(amount):
    d = check_refund_eligibility(Order("A1", 200, 5), amount)
    assert not d.eligible
