"""Lazy-loaded formatters for different front matter formats."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from ._helpers import DuplicateKeyError


class YAMLFormatter:
    """Lazy-loaded YAML formatter using yamlfix."""

    _format_fn: Callable[[str], str] | None = None
    _yaml_module: Any | None = None

    @classmethod
    def format(cls, content: str) -> str:
        """Format YAML content.

        Args:
            content: Raw YAML string to format.

        Returns:
            Formatted YAML string.

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

        """
        if cls._format_fn is None:
            cls._load_formatter()

        # Check for duplicate keys before formatting
        cls._check_duplicate_keys(content)

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
    def _check_duplicate_keys(cls, content: str) -> None:
        """Check for duplicate keys in YAML content.

        Args:
            content: Raw YAML string to check.

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

        """
        if cls._yaml_module is None:
            cls._load_formatter()

        assert cls._yaml_module is not None

        # Create a custom constructor that tracks keys
        class DuplicateKeySafeLoader(cls._yaml_module.SafeLoader):
            pass

        def no_duplicates_constructor(
            loader: Any, node: Any, deep: bool = False,
        ) -> Any:
            """Check for duplicate keys in YAML mappings."""
            mapping = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=deep)
                if key in mapping:
                    raise DuplicateKeyError(str(key), "yaml")
                value = loader.construct_object(value_node, deep=deep)
                mapping[key] = value
            return mapping

        DuplicateKeySafeLoader.add_constructor(
            cls._yaml_module.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            no_duplicates_constructor,
        )

        # Parse with duplicate key detection
        cls._yaml_module.load(content, Loader=DuplicateKeySafeLoader)

    @classmethod
    def _load_formatter(cls) -> None:
        """Lazy-load the yamlfix and yaml libraries."""
        import yaml  # noqa: PLC0415
        import yamlfix  # noqa: PLC0415

        cls._format_fn = yamlfix.fix_code
        cls._yaml_module = yaml


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

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

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
        except Exception as e:
            # Check if this is a duplicate key error from tomli/tomllib
            error_msg = str(e).lower()
            if "cannot overwrite" in error_msg or "duplicate" in error_msg:
                # Extract key name if possible (tomli doesn't give us the key directly)
                # We'll use a generic message
                raise DuplicateKeyError("(unknown key)", "toml") from e
            # If formatting fails for other reasons, return original content
            return content
        else:
            # Remove trailing newline if present
            return formatted.rstrip("\n")

    @staticmethod
    def _sort_dict_recursive(data: Any) -> Any:
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
            }
        if isinstance(data, list):
            return [TOMLFormatter._sort_dict_recursive(item) for item in data]
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

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

        """
        try:
            # Parse with duplicate key detection
            def detect_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
                """Detect duplicate keys in JSON object pairs."""
                seen_keys: set[str] = set()
                result = {}
                for key, value in pairs:
                    if key in seen_keys:
                        raise DuplicateKeyError(key, "json")
                    seen_keys.add(key)
                    result[key] = value
                return result

            parsed = json.loads(content, object_pairs_hook=detect_duplicate_keys)
        except DuplicateKeyError:
            # Re-raise our custom exception
            raise
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
