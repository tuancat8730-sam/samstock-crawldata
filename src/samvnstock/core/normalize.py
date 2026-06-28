import re
from typing import Any

_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name: str) -> str:
    """Convert a camelCase field name (as returned by VN broker APIs) to snake_case."""
    return _CAMEL_BOUNDARY_RE.sub("_", name).lower()


def normalize_keys(record: dict[str, Any]) -> dict[str, Any]:
    """Rename all dict keys from camelCase to snake_case."""
    return {camel_to_snake(key): value for key, value in record.items()}


def remap(raw: dict[str, Any], field_map: dict[str, str]) -> dict[str, Any]:
    """Rename a source's raw field names to the model's field names.

    Keys not present in `field_map` are dropped, so each provider only needs
    to declare the fields its model actually uses.
    """
    return {field_map[key]: value for key, value in raw.items() if key in field_map}


def to_float(value: Any) -> float | None:
    """Parse a numeric field that may arrive as '1,234.5', '', '-', or None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in ("", "-", "N/A"):
        return None
    return float(text)


def to_int(value: Any) -> int | None:
    """Parse an integer field that may arrive as a numeric string, float, or None."""
    parsed = to_float(value)
    return None if parsed is None else int(parsed)
