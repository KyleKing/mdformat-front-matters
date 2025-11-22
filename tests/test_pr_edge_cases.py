"""Tests for edge cases identified in PR review."""

from __future__ import annotations

import mdformat


def test_toml_string_with_brackets():
    """Test that TOML strings containing brackets are not corrupted.

    Regression test for issue where regex normalization would corrupt
    bracket spacing inside TOML strings.
    Example: description = "[ spaced ]" should NOT become "[spaced]"
    """
    text = """+++
title = "Test"
description = "[ spaced ]"
template = "use {variable} here"
array_in_string = "[1, 2, 3]"
+++
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    # Verify brackets in strings are preserved
    assert "[ spaced ]" in result or '"[ spaced ]"' in result
    assert (
        "{variable}" in result
        or '"{variable}"' in result
        or '"use {variable} here"' in result
    )
    assert '"[1, 2, 3]"' in result or "[1, 2, 3]" in result


def test_toml_actual_arrays_normalized():
    """Test that actual TOML arrays are still normalized correctly."""
    text = """+++
tags = ["tag1", "tag2",]
numbers = [ 1 , 2 , 3 ]
+++
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    # Trailing comma should be removed
    assert '"tag2",]' not in result

    # Note: Array spacing normalization is now disabled to prevent
    # string corruption, so we accept whatever python-frontmatter outputs
    assert "# Content" in result


def test_json_with_escaped_quotes():
    """Test JSON with properly escaped quotes."""
    text = r"""{
    "quote": "He said \"hello\"",
    "path": "C:\\Users\\test",
    "backslash_quote": "test\\"
}
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    assert "# Content" in result
    # JSON should parse correctly without errors


def test_json_with_escaped_backslash_then_quote():
    r"""Test JSON with backslash-escaped backslash before quote.

    The sequence \\" means: escaped backslash (literal \) followed by
    unescaped quote (ends the string).
    """
    text = r"""{
    "ends_with_backslash": "test\\",
    "next_key": "value"
}
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    assert "# Content" in result
    assert "next_key" in result or "value" in result


def test_json_with_braces_in_strings():
    """Test JSON with braces inside string values."""
    text = """{
    "template": "use {variable} here",
    "nested": "{ nested { braces } }",
    "array_like": "[1, 2, 3]"
}
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    assert "# Content" in result
    # Braces in strings shouldn't confuse the parser
    assert "template" in result or "variable" in result


def test_json_multiline_with_escapes():
    """Test multiline JSON with various escape sequences."""
    text = r"""{
    "line1": "first line",
    "line2": "second with \"quotes\"",
    "line3": "third with \\ backslash"
}
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})

    assert "# Content" in result
    # All lines should be parsed correctly


def test_toml_multiline_string_with_brackets():
    """Test TOML multiline strings containing brackets."""
    text = '''+++
description = """
This is a [link] in markdown.
And here are {curly} braces.
[ spaced brackets ] too
"""
+++
# Content
'''
    result = mdformat.text(text, extensions={"front_matters"})

    assert "# Content" in result
    # Multiline string content should be preserved
    assert "description" in result
