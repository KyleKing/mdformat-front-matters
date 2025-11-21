"""Front matter formatters using python-frontmatter."""

from __future__ import annotations

import logging
import re
from typing import Any

import frontmatter  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


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

    # Remove trailing commas in arrays (e.g., ["a", "b",] -> ["a", "b"])
    content = re.sub(r",(\s*])", r"\1", content)

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


def _format_with_handler(
    content: str,
    handler: Any,  # frontmatter handler type  # noqa: ANN401
    parse_wrapper: str,
    delimiter: str | None = None,
) -> str:
    """Format front matter using a frontmatter handler.

    Args:
        content: Raw front matter content.
        handler: The frontmatter handler (e.g., YAMLHandler, TOMLHandler).
        parse_wrapper: Template string for wrapping content during parsing.
        delimiter: Delimiter to strip (None for JSON which has special handling).

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


def format_yaml(content: str, *, strict: bool = False) -> str:
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format.
        strict: If True, raise exceptions instead of preserving original.

    Returns:
        Formatted YAML string, or original content if formatting fails
        in non-strict mode.

    Raises:
        ValueError: In strict mode when content has no valid key-value pairs.
        TypeError: In strict mode when content has invalid types.
        AttributeError: In strict mode when content structure is invalid.

    """
    try:
        return _format_with_handler(
            content,
            frontmatter.YAMLHandler(),
            "---\n{content}\n---\n",
            "---",
        )
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug("Failed to format YAML front matter: %s", e)
        if strict:
            raise
        return content
    except Exception as e:  # Catch any other parsing errors
        logger.warning("Unexpected error formatting YAML front matter: %s", e)
        if strict:
            raise
        return content


def format_toml(content: str, *, strict: bool = False) -> str:
    """Format TOML front matter content.

    Args:
        content: Raw TOML string to format.
        strict: If True, raise exceptions instead of preserving original.

    Returns:
        Formatted TOML string, or original content if formatting fails
        in non-strict mode.

    Raises:
        ValueError: In strict mode when content has no valid key-value pairs.
        TypeError: In strict mode when content has invalid types.
        AttributeError: In strict mode when content structure is invalid.

    """
    try:
        formatted = _format_with_handler(
            content,
            frontmatter.TOMLHandler(),
            "+++\n{content}\n+++\n",
            "+++",
        )
        # Normalize TOML output to remove extra blank lines and trailing commas
        return _normalize_toml_output(formatted)
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug("Failed to format TOML front matter: %s", e)
        if strict:
            raise
        return content
    except Exception as e:  # Catch any other parsing errors
        logger.warning("Unexpected error formatting TOML front matter: %s", e)
        if strict:
            raise
        return content


def format_json(content: str, *, strict: bool = False) -> str:
    """Format JSON front matter content.

    Args:
        content: Raw JSON string to format.
        strict: If True, raise exceptions instead of preserving original.

    Returns:
        Formatted JSON string, or original content if formatting fails
        in non-strict mode.

    Raises:
        ValueError: In strict mode when content has no valid key-value pairs.
        TypeError: In strict mode when content has invalid types.
        AttributeError: In strict mode when content structure is invalid.

    """
    try:
        return _format_with_handler(
            content,
            frontmatter.JSONHandler(),
            "{content}\n",
            None,  # JSON has no delimiters
        )
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug("Failed to format JSON front matter: %s", e)
        if strict:
            raise
        return content
    except Exception as e:  # Catch any other parsing errors
        logger.warning("Unexpected error formatting JSON front matter: %s", e)
        if strict:
            raise
        return content
