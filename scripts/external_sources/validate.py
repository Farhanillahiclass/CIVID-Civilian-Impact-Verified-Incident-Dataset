"""
Lightweight schema validation (no jsonschema dependency).
Validates records against schema/external_sources_schema.json: required keys,
enum constraints, and basic type checks. Returns (ok, list_of_errors).
"""
import json
from pathlib import Path
from .config import SCHEMA_DIR

_SCHEMA_PATH = SCHEMA_DIR / "external_sources_schema.json"
_TYPE_MAP = {
    "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "array": list, "object": dict, "null": type(None),
}


def load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_record(rec: dict, schema: dict | None = None) -> tuple[bool, list[str]]:
    schema = schema or load_schema()
    props = schema.get("properties", {})
    required = schema.get("required", [])
    errors: list[str] = []

    for field in required:
        if field not in rec or rec.get(field) is None:
            errors.append(f"missing required field: {field}")

    for field, val in rec.items():
        spec = props.get(field)
        if spec is None:
            continue
        if val is None:
            if "null" not in _types_of(spec):
                errors.append(f"{field}: null not allowed")
            continue
        # type check
        allowed = _types_of(spec)
        py_types = tuple(t for t in (_TYPE_MAP.get(a) for a in allowed) if t)
        # allow int where number expected
        if "number" in allowed and isinstance(val, int):
            pass
        elif not isinstance(val, py_types):
            errors.append(f"{field}: wrong type (got {type(val).__name__}, expected {allowed})")
        # enum check
        if "enum" in spec and val not in spec["enum"]:
            errors.append(f"{field}: value {val!r} not in enum {spec['enum']}")

    return (len(errors) == 0), errors


def _types_of(spec: dict) -> list[str]:
    t = spec.get("type")
    if isinstance(t, list):
        return t
    return [t] if t else []
