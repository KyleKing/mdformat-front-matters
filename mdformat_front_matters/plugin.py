"""Public Extension."""

from __future__ import annotations

import argparse
from collections.abc import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Postprocess, Render

from .mdit_plugins import front_matters_plugin


def add_cli_argument_group(group: argparse._ArgumentGroup) -> None:
    """Add options to the mdformat CLI.

    Stored in `mdit.options["mdformat"]["plugin"]["front_matters"]`

    """
    group.add_argument(
        "--argument",
        action="store_const",
        const=True,
        help="If specified, store true",
    )


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser."""
    mdit.use(front_matters_plugin)


def _render_front_matters(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a `RenderTreeNode`."""
    return node.render(context)


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "<placeholder>": _render_front_matters,
}

# A mapping from `RenderTreeNode.type` to a `Postprocess` that does
# postprocessing for the output of the `Render` function. Unlike
# `Render` funcs, `Postprocess` funcs are collaborative: any number of
# plugins can define a postprocessor for a syntax type and all of them
# will run in series.
POSTPROCESSORS: Mapping[str, Postprocess] = {}
