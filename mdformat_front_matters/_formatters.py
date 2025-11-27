"""Front matter formatters using python-frontmatter."""

from __future__ import annotations

import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import frontmatter  # type: ignore[import-untyped]
import yaml
from mdformat.renderer import LOGGER

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


class _UnicodePreservingYAMLHandler(frontmatter.YAMLHandler):
    """Custom YAML handler that preserves unicode characters without escaping.

    This handler extends the default YAMLHandler to use a custom dumper
    that outputs unicode characters (including emojis) in their original form
    rather than escaping them.
    """

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:  # noqa: PLR6301
        """Export metadata as YAML with unicode preservation.

        Args:
            metadata: Dictionary to export as YAML.
            **kwargs: Additional arguments passed to yaml.dump.

        Returns:
            YAML string with preserved unicode characters.
        """
        sort_keys = kwargs.pop("sort_keys", True)
        """Export metadata as YAML with unicode preservation.

        Args:
            metadata: Dictionary to export as YAML.
            **kwargs: Additional arguments passed to yaml.dump.

        Returns:
            YAML string with preserved unicode characters.
        """

        class UnicodePreservingDumper(yaml.SafeDumper):
            """Custom YAML dumper that preserves unicode in plain style."""

            def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:  # noqa: FBT001, FBT002
                """Override to prevent indentless sequences.

                This ensures YAML sequences (lists) are properly indented with
                spaces before the dash, e.g.:
                    tags:
                      - item
                instead of:
                    tags:
                    - item
                """
                return super().increase_indent(flow, False)

        def str_representer(dumper: Any, data: str) -> Any:  # noqa: ANN401
            """Represent strings with unicode preservation.

            Uses plain style for simple strings with unicode to preserve emojis
            and other unicode characters. Falls back to quoted style for strings
            with special YAML characters.
            """
            # Check if the string needs quoting (has special YAML characters)
            needs_quoting = any(char in data for char in SPECIAL_YAML_CHARS)

            # Also check for leading/trailing whitespace or special patterns
            if (
                needs_quoting
                or data != data.strip()
                or len(data.splitlines()) > 1
                or not data
            ):
                # Let YAML choose the appropriate quoted style
                return dumper.represent_scalar("tag:yaml.org,2002:str", data)

            # Use plain style for simple strings to preserve unicode
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")

        UnicodePreservingDumper.add_representer(str, str_representer)

        kwargs.setdefault("Dumper", UnicodePreservingDumper)
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("allow_unicode", True)
        kwargs["sort_keys"] = sort_keys

        return yaml.dump(metadata, **kwargs).strip()  # type: ignore[call-overload]


class _SortingTOMLHandler(frontmatter.TOMLHandler):
    """Custom TOML handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """Export metadata as TOML with optional key sorting.

        Args:
            metadata: Dictionary to export as TOML.
            **kwargs: Additional arguments.

        Returns:
            TOML string.
        """
        if kwargs.pop("sort_keys", True):
            metadata = dict(sorted(metadata.items()))
        # Call the parent export method
        return super().export(metadata, **kwargs)


class _SortingJSONHandler(frontmatter.JSONHandler):
    """Custom JSON handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """Export metadata as JSON with optional key sorting.

        Args:
            metadata: Dictionary to export as JSON.
            **kwargs: Additional arguments.

        Returns:
            JSON string.
        """
        if kwargs.pop("sort_keys", True):
            metadata = dict(sorted(metadata.items()))
        # Call the parent export method
        return super().export(metadata, **kwargs)


def _normalize_toml_output(content: str) -> str:
    """Normalize TOML output from python-frontmatter.

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
    # The python-frontmatter TOML library already handles spacing correctly.

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
    handler: Any,  # frontmatter handler type  # noqa: ANN401
    parse_wrapper: str,
    delimiter: str | None = None,
    *,
    sort_keys: bool = True,
) -> str:
    """Format front matter using a frontmatter handler.

    Args:
        content: Raw front matter content.
        handler: The frontmatter handler (e.g., YAMLHandler, TOMLHandler).
        parse_wrapper: Template string for wrapping content during parsing.
        delimiter: Delimiter to strip (None for JSON which has special handling).
        sort_keys: Whether to sort keys in the front matter.

    Returns:
        Formatted front matter.

    Raises:
        ValueError: When metadata contains no valid key-value pairs.
    """
    # Parse the content
    metadata, _ = frontmatter.parse(
        parse_wrapper.format(content=content),
        handler=handler,
    )

    # Raise error if no valid metadata to prevent data loss
    # Empty metadata means the content was not valid structured data
    if not metadata:
        msg = "Front matter contains no valid key-value pairs"
        raise ValueError(msg)

    # Create a post and dump back to formatted string
    post = frontmatter.Post("", **metadata)
    if hasattr(handler, "export"):
        # Custom handler like our YAML handler
        formatted = handler.export(metadata, sort_keys=sort_keys)
    else:
        # Standard handlers (TOML, JSON) - they don't support sorting
        formatted = frontmatter.dumps(post, handler=handler)

    # Strip delimiters based on format type
    if delimiter:
        return _strip_delimiters(formatted, delimiter)
    # JSON special handling: extract inner content
    if formatted.startswith("{\n") and formatted.endswith("\n}\n"):
        lines = formatted.split("\n")
        if len(lines) > 2:  # noqa: PLR2004
            inner = "\n".join(lines[1:-2])
            if inner.strip():
                return f"{{\n{inner}\n}}"
    return formatted.rstrip("\n")


def format_yaml(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format.
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.

    Returns:
        Formatted YAML string, or original content if formatting fails
        in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "YAML", strict=strict):
            return _format_with_handler(
                content,
                _UnicodePreservingYAMLHandler(),
                "---\n{content}\n---\n",
                "---",
                sort_keys=sort_keys,
            )
    except FormatError as e:
        return e.content


def format_toml(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format TOML front matter content.

    Args:
        content: Raw TOML string to format.
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically (ignored for TOML).

    Returns:
        Formatted TOML string, or original content if formatting fails
        in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "TOML", strict=strict):
            formatted = _format_with_handler(
                content,
                _SortingTOMLHandler(),
                "+++\n{content}\n+++\n",
                "+++",
                sort_keys=sort_keys,
            )
            return _normalize_toml_output(formatted)
    except FormatError as e:
        return e.content


def format_json(content: str, *, strict: bool = False, sort_keys: bool = True) -> str:
    """Format JSON front matter content.

    Args:
        content: Raw JSON string to format.
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically (ignored for JSON).

    Returns:
        Formatted JSON string, or original content if formatting fails
        in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "JSON", strict=strict):
            return _format_with_handler(
                content,
                _SortingJSONHandler(),
                "{content}\n",
                None,  # JSON has no delimiters
                sort_keys=sort_keys,
            )
    except FormatError as e:
        return e.content
