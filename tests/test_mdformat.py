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


def test_yaml_front_matter_no_sort():
    """Test that YAML front matter preserves key order when sorting is disabled."""
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
z_key: last
a_key: first
m_key: middle
nested:
  z_sub: last
  a_sub: first
---

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"no_sort_front_matter": True}}},
    )
    assert result == expected


def test_toml_front_matter_no_sort():
    """Test that TOML front matter preserves key order when sorting is disabled."""
    input_md = """+++
z_key = "last"
a_key = "first"
m_key = "middle"
+++

Content here.
"""

    expected = """+++
z_key = "last"
a_key = "first"
m_key = "middle"
+++

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"no_sort_front_matter": True}}},
    )
    assert result == expected


def test_json_front_matter_no_sort():
    """Test that JSON front matter preserves key order when sorting is disabled."""
    input_md = """{
"z_key": "last",
"a_key": "first",
"m_key": "middle"
}

Content here.
"""

    expected = """{
    "z_key": "last",
    "a_key": "first",
    "m_key": "middle"
}

Content here.
"""

    result = mdformat.text(
        input_md,
        extensions={"front_matters"},
        options={"plugin": {"front_matters": {"no_sort_front_matter": True}}},
    )
    assert result == expected
