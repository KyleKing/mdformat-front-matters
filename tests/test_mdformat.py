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
