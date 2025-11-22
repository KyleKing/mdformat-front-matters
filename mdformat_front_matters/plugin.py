"""Public Extension."""

from __future__ import annotations

import argparse
from collections.abc import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Postprocess, Render

from ._formatters import format_json, format_toml, format_yaml
from ._helpers import get_conf
from .mdit_plugins import front_matters_plugin


def add_cli_argument_group(group: argparse._ArgumentGroup) -> None:
    """Add options to the mdformat CLI.

    Stored in `mdit.options["mdformat"]["plugin"]["front_matters"]`

    """
    group.add_argument(
        "--strict-front-matter",
        action="store_true",
        help=(
            "Fail on invalid front matter instead of preserving original content. "
            "Useful for CI/CD pipelines to catch formatting errors."
        ),
    )


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to recognize front matter blocks."""
    mdit.use(front_matters_plugin)


def _render_front_matter(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a front matter block.

    Args:
        node: The syntax tree node representing the front matter.
        context: The rendering context.

    Returns:
        Formatted front matter block with appropriate delimiters.

    """
    # Get the format type from node metadata
    format_type = node.meta.get("format", "yaml") if node.meta else "yaml"
    content = node.content
    markup = node.markup

    # Check if strict mode is enabled
    # Note: argparse converts hyphens to underscores, so --strict-front-matter
    # is stored as "strict_front_matter" in the options dict
    strict = bool(get_conf(context.options, "strict_front_matter"))

    # Format the content based on type
    if format_type == "yaml":
        formatted_content = format_yaml(content, strict=strict)
    elif format_type == "toml":
        formatted_content = format_toml(content, strict=strict)
    elif format_type == "json":
        formatted_content = format_json(content, strict=strict)
    else:
        # Unknown format, return as-is
        formatted_content = content

    # Ensure content ends with newline
    if formatted_content and not formatted_content.endswith("\n"):
        formatted_content += "\n"

    # Build the output based on format
    if format_type == "json":
        # JSON front matter has no delimiters
        # Return with single newline; mdformat will add separator
        return formatted_content.rstrip("\n")
    # YAML and TOML have delimiters
    return f"{markup}\n{formatted_content}{markup}"


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "front_matter": _render_front_matter,
}

# A mapping from `RenderTreeNode.type` to a `Postprocess` that does
# postprocessing for the output of the `Render` function. Unlike
# `Render` funcs, `Postprocess` funcs are collaborative: any number of
# plugins can define a postprocessor for a syntax type and all of them
# will run in series.
POSTPROCESSORS: Mapping[str, Postprocess] = {}
