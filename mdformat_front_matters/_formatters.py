"""Front matter formatters for YAML, TOML, and JSON."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
from typing import Any

import toml  # type: ignore[import-untyped]
from mdformat.renderer import LOGGER
from ruamel.yaml import YAML

SPECIAL_YAML_CHARS = {
    ":",
    "{",
    "}",
    "[",
    "]",
    ",",
    "&",
    "*",
    "#",
    "?",
    "|",
    "-",
    "<",
    ">",
    "=",
    "!",
    "%",
    "@",
    "`",
    '"',
    "'",
}
"""These characters require quoting: : { } [ ] , & * # ? | - < > = ! % @ `."""


class _UnicodePreservingYAMLHandler:
    """Custom YAML handler that preserves unicode characters and comments.

    This handler uses ruamel.yaml for round-trip preservation of comments
    and outputs unicode characters (including emojis) in their original form.
    """

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """Export metadata as YAML with unicode and comment preservation.

        Args:
            metadata: Dictionary to export as YAML.
            **kwargs: Additional arguments.

        Returns:
            YAML string with preserved unicode characters and comments.
        """
        sort_keys = kwargs.pop("sort_keys", True)

        yaml = YAML()
        yaml.preserve_quotes = False
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        yaml.width = sys.maxsize  # Prevent line wrapping

        # Consistent indentation for previous mdformat-frontmatter users:
        # https://github.com/butler54/mdformat-frontmatter/blob/93bb972b6044d22043d6c191a2e73858ff09d3e5/mdformat_frontmatter/plugin.py#L14
        yaml.indent(mapping=2, sequence=4, offset=2)

        if sort_keys:
            metadata = self._sort_dict_recursively(metadata)

        stream = StringIO()
        yaml.dump(metadata, stream)
        return stream.getvalue().strip()

    def _sort_dict_recursively(
        self,
        data: dict[str, object],
    ) -> dict[str, object]:
        """Recursively sort dictionary keys.

        Args:
            data: Dictionary to sort.

        Returns:
            Dictionary with sorted keys at all levels.
        """
        sorted_data: dict[str, object] = {}
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, dict):
                sorted_data[key] = self._sort_dict_recursively(value)
            else:
                sorted_data[key] = value
        return sorted_data


class _SortingTOMLHandler:
    """Custom TOML handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:  # noqa: PLR6301
        """Export metadata as TOML with optional key sorting.

        Args:
            metadata: Dictionary to export as TOML.
            **kwargs: Additional arguments (ignored).

        Returns:
            TOML string.
        """
        sort_keys_val = kwargs.pop("sort_keys", True)
        sort_keys = bool(sort_keys_val) if sort_keys_val is not None else True
        if sort_keys:
            metadata = dict(sorted(metadata.items()))
        return toml.dumps(metadata)


class _SortingJSONHandler:
    """Custom JSON handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:  # noqa: PLR6301
        """Export metadata as JSON with optional key sorting.

        Args:
            metadata: Dictionary to export as JSON.
            **kwargs: Additional arguments (ignored).

        Returns:
            JSON string.
        """
        sort_keys_val = kwargs.pop("sort_keys", True)
        sort_keys = bool(sort_keys_val) if sort_keys_val is not None else True
        return json.dumps(metadata, indent=4, sort_keys=sort_keys)


def _normalize_toml_output(content: str) -> str:
    """Normalize TOML output.

    Removes extra blank lines and trailing commas added by the TOML library.

    Args:
        content: TOML content to normalize.

    Returns:
        Normalized TOML content.
    """
    # Remove blank lines before section headers like [section]
    # but NOT array tables [[section]] - they should keep blank lines
    content = re.sub(r"\n\n+(\[(?!\[))", r"\n\1", content)

    # Remove trailing commas in arrays - handle both ,] and , ]
    # This handles: ["a", "b",] and ["a", "b", ] formats
    content = re.sub(r",\s*]", "]", content)

    # NOTE: We do NOT normalize array spacing (e.g., [ "item" -> ["item"])
    # because regex-based approach would corrupt bracket spacing inside strings.
    # Example: description = "[ spaced ]" would incorrectly become "[spaced]"

    # Remove blank line before closing (if present)
    return re.sub(r"\n\n+$", "\n", content)


def _strip_delimiters(formatted: str, delimiter: str) -> str:
    """Strip delimiters from formatted front matter.

    Args:
        formatted: Formatted front matter with delimiters.
        delimiter: The delimiter string (e.g., '---' or '+++').

    Returns:
        Front matter with delimiters removed and trailing newlines stripped.

    """
    formatted = formatted.removeprefix(f"{delimiter}\n")

    # Remove trailing delimiter with or without final newline
    end_with_nl = f"\n{delimiter}\n"
    end_no_nl = f"\n{delimiter}"

    if formatted.endswith(end_with_nl):
        return formatted[: -len(end_with_nl)].rstrip("\n")
    if formatted.endswith(end_no_nl):
        return formatted[: -len(end_no_nl)].rstrip("\n")
    return formatted.rstrip("\n")


class FormatError(Exception):
    """Exception raised when formatting fails and original content should be returned."""

    def __init__(self, content: str) -> None:
        """Initialize with original content to return.

        Args:
            content: Original content to return on formatting failure.
        """
        super().__init__()
        self.content = content


@contextmanager
def _handle_format_errors(
    content: str,
    format_type: str,
    *,
    strict: bool,
) -> Generator[None, None, None]:
    """Handle errors during front matter formatting.

    Args:
        content: Original content to return if formatting fails.
        format_type: Type of format being processed (e.g., 'YAML', 'TOML').
        strict: If True, raise exceptions instead of preserving original.

    Yields:
        None

    Raises:
        FormatError: When formatting fails in non-strict mode (contains original content).
        ValueError: Re-raised in strict mode from parsing/validation failures.
        TypeError: Re-raised in strict mode from invalid content types.
        AttributeError: Re-raised in strict mode from invalid content structure.
    """
    try:
        yield
    except (ValueError, TypeError, AttributeError) as e:
        LOGGER.debug("Failed to format %s front matter: %s", format_type, e)
        if strict:
            raise
        raise FormatError(content) from e
    except Exception as e:
        LOGGER.warning(
            "Unexpected error formatting %s front matter: %s", format_type, e
        )
        if strict:
            raise
        raise FormatError(content) from e


def _format_with_handler(
    content: str,
    handler: Any,  # Handler instance  # noqa: ANN401
    parse_func: Any,  # Parsing function (YAML().load, toml.loads, etc.)  # noqa: ANN401
    *,
    sort_keys: bool = True,
) -> str:
    """Format front matter using a handler and parsing function.

    Args:
        content: Raw front matter content (without delimiters).
        handler: Handler instance with export() method.
        parse_func: Function to parse content (YAML().load, toml.loads, etc.).
        sort_keys: Whether to sort keys in the front matter.

    Returns:
        Formatted front matter (without delimiters).

    Raises:
        TypeError: When metadata is not a dictionary.
        ValueError: When metadata contains no valid key-value pairs.
    """
    metadata = parse_func(content)

    # Metadata must be a dictionary (key-value pairs)
    # Scalar values, lists, etc. are not valid front matter
    if not isinstance(metadata, dict):
        msg = f"Front matter must be key-value pairs, got {type(metadata).__name__}"
        raise TypeError(msg)

    # Allow empty front matter blocks (CommonMark v0.29 spec example 68)
    # Empty content between delimiters is valid and should be preserved
    if not metadata:
        # Only return empty if the original content was truly empty
        if not content.strip():
            return ""
        # For non-empty but unparsable content, raise error to preserve original
        msg = "Front matter contains no valid key-value pairs"
        raise ValueError(msg)

    return handler.export(metadata, sort_keys=sort_keys).strip()


def format_yaml(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.

    Returns:
        Formatted YAML string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "YAML", strict=strict):
            yaml = YAML()
            return _format_with_handler(
                content,
                _UnicodePreservingYAMLHandler(),
                yaml.load,
                sort_keys=sort_keys,
            )
    except FormatError as e:
        return e.content


def format_toml(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format TOML front matter content.

    Args:
        content: Raw TOML string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.

    Returns:
        Formatted TOML string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "TOML", strict=strict):
            formatted = _format_with_handler(
                content,
                _SortingTOMLHandler(),
                toml.loads,
                sort_keys=sort_keys,
            )
            return _normalize_toml_output(formatted)
    except FormatError as e:
        return e.content


def format_json(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format JSON front matter content.

    Args:
        content: Raw JSON string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.

    Returns:
        Formatted JSON string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "JSON", strict=strict):
            return _format_with_handler(
                content,
                _SortingJSONHandler(),
                json.loads,
                sort_keys=sort_keys,
            )
    except FormatError as e:
        return e.content
