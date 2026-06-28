import re
from typing import Any

_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name: str) -> str:
    """Convert a camelCase field name (as returned by VN broker APIs) to snake_case."""
    return _CAMEL_BOUNDARY_RE.sub("_", name).lower()


def normalize_keys(record: dict[str, Any]) -> dict[str, Any]:
    """Rename all dict keys from camelCase to snake_case."""
    return {camel_to_snake(key): value for key, value in record.items()}
