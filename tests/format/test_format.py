from __future__ import annotations

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


fixtures = flatten(
    [
        read_fixture_file(Path(__file__).parent / "fixtures" / fixture_path)
        for fixture_path in (
            "front_matters.md",
            # To determine interoperability with python-frontmatter, copied from:
            #  https://github.com/butler54/mdformat-frontmatter/blob/93bb972b6044d22043d6c191a2e73858ff09d3e5/tests/fixtures.md
            "python_frontmatter.md",
        )
    ],
)


@pytest.mark.parametrize(
    ("line", "title", "text", "expected"),
    fixtures,
    ids=[f[1] for f in fixtures],
)
def test_format_fixtures(line, title, text, expected):
    output = mdformat.text(text, extensions={"front_matters"})
    print_text(output, expected)
    assert output.rstrip() == expected.rstrip()
