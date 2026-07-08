"""Offline tests for tool-schemas. stdlib + pytest only; no network, no key."""
from __future__ import annotations

from toolschemas import catalog_tokens, estimate_tokens, is_valid, trim, validate

WEATHER = {
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}
REFUND = {
    "name": "issue_refund",
    "description": "Issue a refund for an order.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
        "required": ["order_id", "amount"],
        "additionalProperties": False,
    },
}


def test_estimate_tokens_scales_with_length():
    assert estimate_tokens("a" * 40) > estimate_tokens("a" * 4)
    assert estimate_tokens("") >= 1


def test_catalog_tokens_monotonic_in_catalogue_size():
    full = catalog_tokens([WEATHER, REFUND])
    trimmed = catalog_tokens(trim([WEATHER, REFUND], keep=1))
    assert trimmed < full  # fewer tools -> fewer tokens


def test_validate_accepts_a_good_payload():
    payload = {"city": "Paris", "unit": "celsius"}
    assert is_valid(payload, WEATHER["input_schema"])
    assert validate(payload, WEATHER["input_schema"]) == []


def test_validate_rejects_missing_required():
    errs = validate({"unit": "celsius"}, WEATHER["input_schema"])
    assert any("missing required property 'city'" in e for e in errs)


def test_validate_rejects_wrong_type():
    errs = validate({"order_id": "x", "amount": "free"}, REFUND["input_schema"])
    assert any("expected number" in e for e in errs)


def test_validate_rejects_additional_property():
    errs = validate({"city": "Paris", "nope": 1}, WEATHER["input_schema"])
    assert any("additional property 'nope'" in e for e in errs)


def test_validate_rejects_bad_enum():
    errs = validate({"city": "Paris", "unit": "kelvin"}, WEATHER["input_schema"])
    assert any("not in enum" in e for e in errs)


def test_validate_rejects_bool_as_number():
    # bool must not satisfy integer/number, matching JSON Schema semantics
    errs = validate({"order_id": "x", "amount": True}, REFUND["input_schema"])
    assert any("expected number" in e for e in errs)
