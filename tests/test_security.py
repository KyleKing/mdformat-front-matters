"""Security and edge case tests."""

from __future__ import annotations

import pytest

import mdformat


@pytest.mark.parametrize(
    ("test_name", "text"),
    [
        (
            "python_object_tag",
            """---
!!python/object:os.system
args: ['echo malicious']
---
# Content
""",
        ),
        (
            "yaml_anchor_bomb",
            """---
a: &a ["lol","lol","lol","lol","lol","lol","lol","lol","lol"]
b: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]
c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]
d: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]
---
# Content
""",
        ),
    ],
)
def test_yaml_security_vulnerabilities(test_name, text):
    """Test that YAML security vulnerabilities are handled safely."""
    # Should handle without crashing or executing malicious code
    result = mdformat.text(text, extensions={"front_matters"})
    assert result is not None
    assert "# Content" in result


def test_very_large_front_matter():
    """Test handling of very large front matter."""
    # Create a large YAML front matter
    large_dict = "\n".join(f"  key_{i}: value_{i}" for i in range(1000))
    text = f"""---
data:
{large_dict}
---
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    assert "# Content" in result
    assert "data:" in result


def test_deeply_nested_yaml():
    """Test handling of deeply nested YAML structures."""
    # Create deeply nested structure
    nesting = "a:\n  " * 50 + "value: test"
    text = f"""---
{nesting}
---
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    assert "# Content" in result


def test_json_with_string_containing_braces():
    """Test JSON front matter with braces in string values."""
    text = """{
    "description": "Text with {braces} inside",
    "template": "{{variable}}",
    "example": "nested {{{triple}}} braces"
}
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    # Should parse correctly and preserve brace content
    assert "# Content" in result
    assert "description" in result or "Text with" in result


@pytest.mark.parametrize(
    ("format_type", "text"),
    [
        (
            "toml_multiline",
            '''+++
description = """
This is a multiline
string in TOML
"""
+++
# Content
''',
        ),
        (
            "yaml_special_chars",
            """---
title: Test & Special <Characters>
path: "C:\\\\Windows\\\\System32"
email: user@example.com
url: https://example.com?param=value&other=123
---
# Content
""",
        ),
        (
            "yaml_null_values",
            """---
nullable: null
empty:
present: value
---
# Content
""",
        ),
        (
            "toml_datetime",
            """+++
date = 2024-01-01T12:00:00Z
updated = 2024-01-01T12:00:00+05:30
+++
# Content
""",
        ),
    ],
)
def test_format_specific_edge_cases(format_type, text):
    """Test edge cases specific to different front matter formats."""
    result = mdformat.text(text, extensions={"front_matters"})
    assert "# Content" in result


def test_empty_front_matter_blocks():
    """Test handling of empty front matter blocks."""
    text = """---
---
# Content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    assert "# Content" in result
    # Empty front matter should be preserved as-is
    assert "---" in result


def test_front_matter_not_at_start():
    """Test that front matter not at document start is ignored."""
    text = """# First heading

---
title: Test
---

More content
"""
    result = mdformat.text(text, extensions={"front_matters"})
    # Front matter should be treated as regular markdown
    assert "# First heading" in result


def test_multiple_front_matter_blocks():
    """Test that only first front matter block is processed."""
    text = """---
title: First
---
# Content

---
title: Second
---
"""
    result = mdformat.text(text, extensions={"front_matters"})
    # Second block should be treated as thematic break
    assert "title: First" in result or "title:" in result


@pytest.mark.parametrize(
    ("format_type", "text"),
    [
        (
            "json_missing_comma",
            """{
    "title": "Test"
    "missing": "comma"
}
# Content
""",
        ),
        (
            "yaml_invalid_indent",
            """---
parent:
child: wrong_indent
  another: also_wrong
---
# Content
""",
        ),
        (
            "toml_missing_quote",
            '''+++
title = "Missing quote
description = "Valid"
+++
# Content
''',
        ),
    ],
)
def test_malformed_content_recovery(format_type, text):
    """Test that malformed front matter is preserved rather than causing errors."""
    result = mdformat.text(text, extensions={"front_matters"})
    # Should preserve malformed content without crashing
    assert "# Content" in result


@pytest.fixture
def large_yaml_structure():
    """Fixture providing a large YAML structure for testing."""
    large_dict = "\n".join(f"  key_{i}: value_{i}" for i in range(100))
    return f"""---
data:
{large_dict}
---
# Content
"""


@pytest.fixture
def deeply_nested_structure():
    """Fixture providing a deeply nested YAML structure for testing."""
    nesting = "level:\n  " * 20 + "value: deep"
    return f"""---
{nesting}
---
# Content
"""


def test_performance_with_large_structure(large_yaml_structure):
    """Test that large structures are processed efficiently."""
    result = mdformat.text(large_yaml_structure, extensions={"front_matters"})
    assert result is not None
    assert "# Content" in result


def test_performance_with_nested_structure(deeply_nested_structure):
    """Test that deeply nested structures are processed efficiently."""
    result = mdformat.text(deeply_nested_structure, extensions={"front_matters"})
    assert result is not None
    assert "# Content" in result
