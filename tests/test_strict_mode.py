"""Tests for strict mode functionality."""

from __future__ import annotations

import pytest

import mdformat


def test_strict_mode_with_invalid_yaml():
    """Test that strict mode raises an error for invalid YAML."""
    text = """---
] This is a YAML parse error
---
# Content
"""
    # Default mode should preserve content
    result = mdformat.text(text, extensions={"front_matters"})
    assert "] This is a YAML parse error" in result

    # Strict mode should raise an error
    with pytest.raises(Exception):  # Could be various exception types
        mdformat.text(
            text,
            extensions={"front_matters"},
            options={"strict_front_matter": True},
        )


def test_strict_mode_with_empty_front_matter():
    """Test that strict mode raises an error for empty front matter (no key-value pairs)."""
    text = """---
Foo
---
# Content
"""
    # Default mode should preserve content
    result = mdformat.text(text, extensions={"front_matters"})
    assert "Foo" in result

    # Strict mode should raise ValueError (empty metadata)
    with pytest.raises(ValueError):
        mdformat.text(
            text,
            extensions={"front_matters"},
            options={"strict_front_matter": True},
        )


def test_strict_mode_with_valid_yaml():
    """Test that strict mode works normally with valid YAML."""
    text = """---
title: Test
description: Valid YAML
---
# Content
"""
    # Both modes should work fine
    result_default = mdformat.text(text, extensions={"front_matters"})
    result_strict = mdformat.text(
        text,
        extensions={"front_matters"},
        options={"strict_front_matter": True},
    )

    assert "title:" in result_default
    assert "title:" in result_strict
    assert "# Content" in result_default
    assert "# Content" in result_strict


def test_strict_mode_with_invalid_toml():
    """Test that strict mode raises an error for invalid TOML."""
    text = '''+++
title = "Missing quote
description = "Valid"
+++
# Content
'''
    # Default mode should preserve content
    result = mdformat.text(text, extensions={"front_matters"})
    assert 'title = "Missing quote' in result

    # Strict mode should raise an error
    with pytest.raises(Exception):
        mdformat.text(
            text,
            extensions={"front_matters"},
            options={"strict_front_matter": True},
        )


def test_strict_mode_with_invalid_json():
    """Test that strict mode raises an error for invalid JSON."""
    text = """{
    "title": "Test"
    "missing": "comma"
}
# Content
"""
    # Default mode should preserve content
    result = mdformat.text(text, extensions={"front_matters"})
    assert '"title": "Test"' in result

    # Strict mode should raise an error
    with pytest.raises(Exception):
        mdformat.text(
            text,
            extensions={"front_matters"},
            options={"strict_front_matter": True},
        )


@pytest.mark.parametrize(
    "text",
    [
        # Valid YAML
        """---
title: Test
tags:
  - a
  - b
---
# Content
""",
        # Valid TOML
        """+++
title = "Test"
tags = ["a", "b"]
+++
# Content
""",
        # Valid JSON
        """{
    "title": "Test",
    "tags": ["a", "b"]
}
# Content
""",
    ],
)
def test_strict_mode_accepts_valid_content(text):
    """Test that strict mode accepts all valid front matter formats."""
    result = mdformat.text(
        text,
        extensions={"front_matters"},
        options={"strict_front_matter": True},
    )
    assert "# Content" in result
    assert "title" in result.lower()


def test_strict_mode_false_by_default():
    """Test that strict mode is disabled by default."""
    # This should not raise
    text = """---
invalid YAML without key-value pairs
---
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    assert result is not None
    assert "# Content" in result
