from pathlib import Path

import mdformat
import pytest


@pytest.mark.parametrize("format_type", ["yaml", "toml", "json"])
def test_mdformat_text(format_type):
    """Verify that using mdformat works as expected for all frontmatter formats."""
    pth = Path(__file__).parent / f"pre-commit-test-{format_type}.md"
    content = pth.read_text()

    result = mdformat.text(content, extensions={"front_matters"})

    pth.write_text(result)  # Easier to debug with git
    assert result == content, (
        f"Differences found in format for {format_type}. Review in git."
    )


def test_yaml_front_matter_with_sort():
    """Test that YAML front matter sorts keys when --sort-front-matter is enabled."""
    input_md = """---
z_key: last
a_key: first
m_key: middle
nested:
  z_sub: last
  a_sub: first
---

Content here.
"""

    expected = """---
a_key: first
m_key: middle
nested:
  a_sub: first
  z_sub: last
z_key: last
---

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )
    assert result == expected


def test_toml_front_matter_with_sort():
    """Test that TOML front matter sorts keys when --sort-front-matter is enabled."""
    input_md = """+++
z_key = "last"
a_key = "first"
m_key = "middle"
+++

Content here.
"""

    expected = """+++
a_key = "first"
m_key = "middle"
z_key = "last"
+++

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )
    assert result == expected


def test_json_front_matter_with_sort():
    """Test that JSON front matter sorts keys when --sort-front-matter is enabled."""
    input_md = """{
"z_key": "last",
"a_key": "first",
"m_key": "middle"
}

Content here.
"""

    expected = """{
    "a_key": "first",
    "m_key": "middle",
    "z_key": "last"
}

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )
    assert result == expected


def test_yaml_comments_preserved_with_sort():
    """Test that YAML comments are preserved when sorting is enabled."""
    input_md = """---
# Configuration section
z_key: last  # This should move
a_key: first  # This should be first
# Middle section comment
m_key: middle
nested:
  z_sub: last  # nested comment
  a_sub: first
---

Content here.
"""

    # Expected: keys sorted but comments preserved
    expected = """---
# Configuration section
a_key: first  # This should be first
# Middle section comment
m_key: middle
nested:
  a_sub: first
  z_sub: last  # nested comment
z_key: last  # This should move
---

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )
    assert result == expected


def test_yaml_block_comments_preserved_with_sort():
    """Test that YAML block comments are preserved when sorting is enabled.

    Note: Standalone block comments (on separate lines) may not maintain their
    exact position relative to keys after sorting, as they are attached to line
    numbers rather than specific keys in YAML's internal representation.
    Header comments are preserved.
    """
    input_md = """---
# This is the header comment

z_field: value1
# Comment before middle field
m_field: value2
a_field: value3
---

Content.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )

    # Header comment should be preserved
    assert "# This is the header comment" in result
    # All keys should be sorted
    lines = result.split("\n")
    key_lines = [l for l in lines if l and not l.startswith("#") and ":" in l]
    assert key_lines == ["a_field: value3", "m_field: value2", "z_field: value1"]
    # Block comment should be preserved (though position may vary)
    assert "# Comment before middle field" in result


def test_yaml_comments_preserved_with_strict_mode():
    """Test that YAML comments are preserved when strict mode is enabled."""
    input_md = """---
# Main configuration
title: Test  # inline comment
# Section marker
description: A test document
tags:
  - python  # programming language
  - yaml  # config format
---

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"strict_front_matter": True}}},
    )

    # All comments should be preserved
    assert "# Main configuration" in result
    assert "# inline comment" in result
    assert "# Section marker" in result
    assert "# programming language" in result
    assert "# config format" in result


def test_yaml_standalone_block_comments_edge_case():
    """Demonstrate known limitation: standalone block comments may move when sorting.

    This test documents that standalone block comments (on separate lines between
    keys) don't maintain their exact association with the following key after sorting.
    This is because YAML's internal representation attaches these comments to line
    numbers or preceding elements, not to specific following keys.

    End-of-line comments (inline comments) DO maintain their association and are
    the recommended approach when sorting is needed.
    """
    input_md = """---
z_field: value1
# This comment is before m_field
m_field: value2
a_field: value3
---

Content.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"sort_front_matter": True}}},
    )

    # Keys should be sorted correctly
    lines = result.split("\n")
    key_lines = [l for l in lines if l and not l.startswith("#") and ":" in l]
    assert key_lines == ["a_field: value3", "m_field: value2", "z_field: value1"]

    # Comment is preserved but may not be in its original position
    assert "# This comment is before m_field" in result

    # Verify the actual output shows the limitation
    # The comment moves to a different position after sorting
    expected_actual = """---
a_field: value3
m_field: value2
z_field: value1
# This comment is before m_field
---

Content.
"""
    assert result == expected_actual
