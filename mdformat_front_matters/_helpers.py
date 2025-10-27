"""General Helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from . import __plugin_name__

ContextOptions = Mapping[str, Any]


class DuplicateKeyError(ValueError):
    """Raised when duplicate keys are detected in front matter."""

    def __init__(self, key: str, format_type: str) -> None:
        """Initialize the error with the duplicate key and format type.

        Args:
            key: The duplicate key name.
            format_type: The format type (yaml, toml, json).

        """
        msg = f"Duplicate key '{key}' found in {format_type.upper()} front matter"
        super().__init__(msg)
        self.key = key
        self.format_type = format_type


def get_conf(options: ContextOptions, key: str) -> bool | str | int | None:
    """Read setting from mdformat configuration Context."""
    if (api := options["mdformat"].get(key)) is not None:
        return api  # From API
    return (
        options["mdformat"].get("plugin", {}).get(__plugin_name__, {}).get(key)
    )  # from cli_or_toml


def should_sort_keys(options: ContextOptions) -> bool:
    """Check if keys should be sorted (default: True).

    Args:
        options: mdformat configuration context.

    Returns:
        True if keys should be sorted, False otherwise.

    """
    no_sort = get_conf(options, "no_sort_keys")
    # If no_sort_keys is set to True, return False (don't sort)
    # Otherwise return True (sort by default)
    return not bool(no_sort)
