"""Front matter formatters using python-frontmatter."""

from __future__ import annotations

from typing import Any

import frontmatter  # type: ignore[import-untyped]


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

    """
    # Parse the content
    metadata, _ = frontmatter.parse(
        parse_wrapper.format(content=content),
        handler=handler,
    )

    # Return empty string if no metadata
    if not metadata:
        return ""

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


def format_yaml(content: str) -> str:
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format.

    Returns:
        Formatted YAML string, or original content if formatting fails.

    """
    try:
        return _format_with_handler(
            content,
            frontmatter.YAMLHandler(),
            "---\n{content}\n---\n",
            "---",
        )
    except Exception:
        return content


def format_toml(content: str) -> str:
    """Format TOML front matter content.

    Args:
        content: Raw TOML string to format.

    Returns:
        Formatted TOML string, or original content if formatting fails.

    """
    try:
        return _format_with_handler(
            content,
            frontmatter.TOMLHandler(),
            "+++\n{content}\n+++\n",
            "+++",
        )
    except Exception:
        return content


def format_json(content: str) -> str:
    """Format JSON front matter content.

    Args:
        content: Raw JSON string to format.

    Returns:
        Formatted JSON string, or original content if formatting fails.

    """
    try:
        return _format_with_handler(
            content,
            frontmatter.JSONHandler(),
            "{content}\n",
            None,  # JSON has no delimiters
        )
    except Exception:
        return content
