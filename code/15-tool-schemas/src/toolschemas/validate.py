"""A minimal JSON-Schema validator for structured output.

Structured output only helps if you actually *check* it (Post 21). This is a tiny,
dependency-free validator covering the subset of JSON Schema a tool call uses:
``type``, ``required``, ``properties``, ``enum``, ``additionalProperties: false``,
and array ``items``. It returns a list of human-readable errors (empty = valid) so
it slots straight into a validate-and-retry loop.

For production use ``jsonschema`` or a Pydantic model (see README, the ``schema``
extra); this exists so the teaching example runs and tests with no dependencies.
"""
from __future__ import annotations

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value, type_name: str) -> bool:
    # bool is a subclass of int in Python; keep them distinct like JSON Schema does.
    if type_name == "integer" and isinstance(value, bool):
        return False
    if type_name == "number" and isinstance(value, bool):
        return False
    return isinstance(value, _TYPES[type_name])


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Return a list of validation error strings; an empty list means the instance is valid."""
    errors: list[str] = []
    t = schema.get("type")
    if t and not _type_ok(instance, t):
        errors.append(f"{path}: expected {t}, got {type(instance).__name__}")
        return errors  # further checks assume the type held

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    if t == "object":
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property '{req}'")
        props = schema.get("properties", {})
        for key, val in instance.items():
            if key in props:
                errors += validate(val, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property '{key}' is not allowed")

    if t == "array" and "items" in schema:
        for i, item in enumerate(instance):
            errors += validate(item, schema["items"], f"{path}[{i}]")

    return errors


def is_valid(instance, schema: dict) -> bool:
    return not validate(instance, schema)
