"""Small text/tag normalization helpers shared across ingestion and services."""

from typing import Any


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
