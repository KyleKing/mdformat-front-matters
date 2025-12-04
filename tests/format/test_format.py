from __future__ import annotations

import json
import re
from itertools import chain
from pathlib import Path
from typing import TypeVar

import mdformat
import pytest
from markdown_it.utils import read_fixture_file

from tests.helpers import print_text

T = TypeVar("T")


def flatten(nested_list: list[list[T]]) -> list[T]:
    return [*chain(*nested_list)]


def _extract_options_from_title(title: str) -> tuple[str, dict[str, object]]:
    r"""Extract mdformat options from test title.

    Supports newline-separated JSON: "Test name\n{\"option\": true}"
    If no JSON found, returns empty dict.

    Args:
        title: Test title, possibly containing JSON options.

    Returns:
        Tuple of (cleaned_title, options_dict).
    """
    if "\n" in title and (match := re.search(r"\n(\{.*\})\s*$", title)):
        json_str = match.group(1)
        clean_title = title[: match.start()].strip()
        try:
            options = json.loads(json_str)
        except json.JSONDecodeError:
            return title, {}
        else:
            return clean_title, {"plugin": {"front_matters": options}}

    return title, {}  # No options found


fixtures = flatten(
    [
        read_fixture_file(Path(__file__).parent / "fixtures" / fixture_path)
        for fixture_path in (
            "front_matters.md",
            "comment_preservation.md",
            "sorting.md",
            # From: https://gohugo.io/content-management/front-matter
            "hugo.md",
            # To determine interoperability with mdformat-frontmatter, copied from:
            #  https://github.com/butler54/mdformat-frontmatter/blob/93bb972b6044d22043d6c191a2e73858ff09d3e5/tests/fixtures.md
            "mdformat_frontmatter.md",
        )
    ],
)


@pytest.mark.parametrize(
    ("line", "title", "text", "expected"),
    fixtures,
    ids=[_extract_options_from_title(f[1])[0] for f in fixtures],
)
def test_format_fixtures(line, title, text, expected):
    _clean_title, options = _extract_options_from_title(title)

    output = mdformat.text(text, extensions={"front_matters"}, options=options or {})

    print_text(output, expected)
    assert output.rstrip() == expected.rstrip()
