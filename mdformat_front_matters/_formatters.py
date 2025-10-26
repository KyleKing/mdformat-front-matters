"""Lazy-loaded formatters for different front matter formats."""

from __future__ import annotations

import json
import sys
import types
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class YAMLFormatter:
    """Lazy-loaded YAML formatter using yamlfix."""

    _format_fn: Callable[[str], str] | None = None
    _yaml_module: types.ModuleType | None = None

    @classmethod
    def format(cls, content: str) -> str:
        """Format YAML content.

        Args:
            content: Raw YAML string to format.

        Returns:
            Formatted YAML string.

        """
        if cls._format_fn is None:
            cls._load_formatter()

        try:
            # yamlfix.fix_code returns formatted YAML
            assert cls._format_fn is not None
            formatted = cls._format_fn(content)
            # yamlfix adds a YAML document start marker (---), remove it
            if formatted.startswith("---\n"):
                formatted = formatted[4:]
            elif formatted.startswith("--- "):
                # Handle scalar values like "--- Foo\n...\n"
                formatted = formatted[4:]
            # Remove YAML document end marker (...) if present
            if formatted.endswith("\n...\n"):
                formatted = formatted[:-5]
            elif formatted.endswith("\n..."):
                formatted = formatted[:-4]
            # Remove trailing newline if present
            formatted = formatted.rstrip("\n")
            # Handle empty content (YAML represents it as null)
            if not formatted.strip():
                return "null"
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            return formatted

    @classmethod
    def _load_formatter(cls) -> None:
        """Lazy-load the yamlfix library."""
        import yamlfix  # noqa: PLC0415

        cls._format_fn = yamlfix.fix_code


class TOMLFormatter:
    """Lazy-loaded TOML formatter using tomli/tomli-w."""

    _loads_fn: Callable[[str], dict[str, Any]] | None = None
    _dumps_fn: Callable[[dict[str, Any]], str] | None = None

    @classmethod
    def format(cls, content: str) -> str:
        """Format TOML content.

        Args:
            content: Raw TOML string to format.

        Returns:
            Formatted TOML string.

        """
        if cls._loads_fn is None or cls._dumps_fn is None:
            cls._load_formatter()

        try:
            # Parse and re-dump to format
            assert cls._loads_fn is not None
            assert cls._dumps_fn is not None
            parsed = cls._loads_fn(content)
            parsed = cls._sort_dict_recursive(parsed)
            formatted = cls._dumps_fn(parsed)
            # tomli-w uses space in datetimes, but TOML spec prefers T
            # Replace datetime spaces with T for better compatibility
            formatted = cls._normalize_datetimes(formatted)
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            # Remove trailing newline if present
            return formatted.rstrip("\n")

    @staticmethod
    def _sort_dict_recursive(data: T) -> T:
        """Recursively sort dictionaries by their keys.

        Args:
            data: Data structure to sort (can be dict, list, or other types).

        Returns:
            Sorted data structure with all nested dicts sorted by keys.

        """
        if isinstance(data, dict):
            return {
                k: TOMLFormatter._sort_dict_recursive(v)
                for k, v in sorted(data.items())
            }  # type: ignore[return-value]
        if isinstance(data, list):
            return [TOMLFormatter._sort_dict_recursive(item) for item in data]  # type: ignore[return-value]
        return data

    @staticmethod
    def _normalize_datetimes(toml_str: str) -> str:
        """Normalize datetime formatting to use T instead of space.

        Args:
            toml_str: TOML string with potential datetime values.

        Returns:
            TOML string with normalized datetime format.

        """
        import re  # noqa: PLC0415

        # Match datetime patterns like "2024-02-02 04:14:54"
        # and replace space with T
        pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})"
        return re.sub(pattern, r"\1T\2", toml_str)

    @classmethod
    def _load_formatter(cls) -> None:
        """Lazy-load the tomli/tomli-w libraries."""
        # Use tomllib for Python 3.11+, tomli for older versions
        if sys.version_info >= (3, 11):
            import tomllib  # noqa: PLC0415

            cls._loads_fn = tomllib.loads
        else:
            import tomli  # type: ignore[import-not-found]  # noqa: PLC0415

            cls._loads_fn = tomli.loads

        import tomli_w  # noqa: PLC0415

        cls._dumps_fn = tomli_w.dumps


class JSONFormatter:
    """JSON formatter using standard library."""

    @staticmethod
    def format(content: str) -> str:
        """Format JSON content.

        Args:
            content: Raw JSON string to format.

        Returns:
            Formatted JSON string with 2-space indentation.

        """
        try:
            # Parse and re-dump with 2-space indentation
            parsed = json.loads(content)
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
