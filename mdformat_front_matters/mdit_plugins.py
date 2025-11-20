"""Markdown-it plugin for multi-format front matter blocks.

Supports:
- YAML front matter (delimited by ---)
- TOML front matter (delimited by +++)
- JSON front matter (delimited by {...})
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from markdown_it import MarkdownIt
    from markdown_it.rules_block import StateBlock
    from markdown_it.token import Token

# Regex patterns for detecting front matter delimiters
YAML_DELIMITER_PATTERN = re.compile(r"^-{3,}(\s*)$")
TOML_DELIMITER_PATTERN = re.compile(r"^\+{3,}(\s*)$")
JSON_OPENING_PATTERN = re.compile(r"^\s*\{\s*$")


def front_matters_plugin(md: MarkdownIt) -> None:
    """Plugin to parse YAML, TOML, and JSON front matter blocks.

    Args:
        md: The markdown-it parser instance to modify.

    """
    md.block.ruler.before(
        "fence",
        "front_matter",
        _front_matter_rule,
        {"alt": ["paragraph", "reference", "blockquote", "list"]},
    )
    # Add renderer for HTML output (front matter should not appear in HTML)
    md.add_render_rule("front_matter", _render_front_matter_html)


def _render_front_matter_html(
    _tokens: list[Token],
    _idx: int,
    _options: dict[str, Any],
    _env: dict[str, Any],
    _renderer: Any,  # markdown-it renderer type not well-defined  # noqa: ANN401
) -> str:
    """Render front matter token to HTML (returns empty string).

    Front matter is metadata and should not appear in HTML output.

    Args:
        _tokens: List of tokens (unused).
        _idx: Index of current token (unused).
        _options: Renderer options (unused).
        _env: Environment variables (unused).
        _renderer: The renderer instance (unused).

    Returns:
        Empty string.

    """
    return ""


def _front_matter_rule(  # noqa: C901, PLR0914
    state: StateBlock,
    start_line: int,
    end_line: int,
    silent: bool,
) -> bool:
    """Block rule to detect and parse front matter blocks.

    Args:
        state: The current parser state.
        start_line: Starting line number.
        end_line: Ending line number.
        silent: If True, only check if the rule matches without creating tokens.

    Returns:
        True if front matter was found and parsed, False otherwise.

    """
    # Front matter must be at the start of the document
    if start_line != 0:
        return False

    pos = state.bMarks[start_line] + state.tShift[start_line]
    maximum = state.eMarks[start_line]

    # Get the first line content
    first_line = state.src[pos:maximum]

    # Detect format based on opening delimiter
    yaml_match = YAML_DELIMITER_PATTERN.match(first_line)
    toml_match = TOML_DELIMITER_PATTERN.match(first_line)
    json_match = JSON_OPENING_PATTERN.match(first_line)

    # Check for minimum length (only for YAML/TOML)
    if not json_match and pos + 3 > maximum:
        return False

    if yaml_match:
        markup = first_line.rstrip()
        format_type = "yaml"
    elif toml_match:
        markup = first_line.rstrip()
        format_type = "toml"
    elif json_match:
        return _parse_json_front_matter(state, start_line, end_line, silent)
    else:
        return False

    # Find closing delimiter for YAML/TOML
    auto_closed = False
    next_line = start_line + 1

    # Search for the closing marker
    while next_line < end_line:
        pos = state.bMarks[next_line] + state.tShift[next_line]
        maximum = state.eMarks[next_line]

        if pos < maximum and state.sCount[next_line] < state.blkIndent:
            # non-empty line with negative indent should stop the block
            break

        line_content = state.src[pos:maximum]
        closing_match = re.match(
            rf"^{re.escape(markup[0])}{{{len(markup)},}}(\s*)$",
            line_content,
        )

        if closing_match:
            auto_closed = True
            break

        next_line += 1

    if not auto_closed:
        return False

    old_line_max = state.lineMax
    old_parent = state.parentType
    state.parentType = "front_matter"

    # Extract content between delimiters (preserve indentation)
    content_lines = []
    for line_num in range(start_line + 1, next_line):
        pos = state.bMarks[line_num]
        maximum = state.eMarks[line_num]
        content_lines.append(state.src[pos:maximum])

    content = "\n".join(content_lines)

    if not silent:
        token = state.push("front_matter", "", 0)
        token.content = content
        token.markup = markup
        token.map = [start_line, next_line + 1]
        token.meta = {"format": format_type}

    state.parentType = old_parent
    state.lineMax = old_line_max
    state.line = next_line + 1

    return True


def _parse_json_front_matter(
    state: StateBlock,
    start_line: int,
    end_line: int,
    silent: bool,
) -> bool:
    """Parse JSON front matter block.

    Args:
        state: The current parser state.
        start_line: Starting line number.
        end_line: Ending line number.
        silent: If True, only check if the rule matches without creating tokens.

    Returns:
        True if JSON front matter was found and parsed, False otherwise.

    """
    # Find the closing brace
    pos = state.bMarks[start_line] + state.tShift[start_line]
    content_lines = []
    brace_count = 0
    next_line = start_line
    in_string = False
    escape_next = False

    # Collect lines until we find the closing brace
    while next_line < end_line:
        pos = state.bMarks[next_line] + state.tShift[next_line]
        maximum = state.eMarks[next_line]
        line_content = state.src[pos:maximum]

        content_lines.append(line_content)

        # Count braces to find the closing one, respecting string context
        for char in line_content:
            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
            elif not in_string:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        # Found closing brace
                        if not silent:
                            content = "\n".join(content_lines)
                            token = state.push("front_matter", "", 0)
                            token.content = content
                            token.markup = ""
                            token.map = [start_line, next_line + 1]
                            token.meta = {"format": "json"}

                        state.line = next_line + 1
                        return True

        next_line += 1

    # No closing brace found
    return False
