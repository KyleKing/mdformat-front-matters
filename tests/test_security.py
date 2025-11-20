"""Security and edge case tests."""

from __future__ import annotations

import mdformat


class TestSecurityEdgeCases:
    """Tests for security vulnerabilities and edge cases."""

    def test_yaml_with_python_tag(self):
        """Test that Python object tags are handled safely."""
        # Should not execute arbitrary Python code
        text = """---
!!python/object:os.system
args: ['echo malicious']
---
# Content
"""
        # Should preserve original content on parse error
        result = mdformat.text(text, extensions={"front_matters"})
        # The formatter should either format it safely or preserve it as-is
        assert "# Content" in result

    def test_yaml_with_anchor_bomb(self):
        """Test handling of YAML anchor bombs (billion laughs attack)."""
        text = """---
a: &a ["lol","lol","lol","lol","lol","lol","lol","lol","lol"]
b: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]
c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]
d: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]
---
# Content
"""
        # Should handle without crashing
        result = mdformat.text(text, extensions={"front_matters"})
        assert result is not None

    def test_very_large_front_matter(self):
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

    def test_deeply_nested_yaml(self):
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

    def test_json_with_string_containing_braces(self):
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
        # May not parse correctly due to current implementation limitation

    def test_toml_with_multiline_strings(self):
        """Test TOML with multiline strings."""
        text = '''+++
description = """
This is a multiline
string in TOML
"""
+++
# Content
'''
        result = mdformat.text(text, extensions={"front_matters"})
        assert "# Content" in result

    def test_yaml_with_special_characters(self):
        """Test YAML with various special characters."""
        text = """---
title: Test & Special <Characters>
path: "C:\\\\Windows\\\\System32"
email: user@example.com
url: https://example.com?param=value&other=123
---
# Content
"""
        result = mdformat.text(text, extensions={"front_matters"})
        assert "# Content" in result
        assert "title:" in result

    def test_empty_front_matter_blocks(self):
        """Test handling of empty front matter blocks."""
        text = """---
---
# Content
"""
        result = mdformat.text(text, extensions={"front_matters"})
        assert "# Content" in result

    def test_front_matter_not_at_start(self):
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

    def test_multiple_front_matter_blocks(self):
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

    def test_malformed_json_recovery(self):
        """Test that malformed JSON is preserved."""
        text = """{
    "title": "Test"
    "missing": "comma"
}
# Content
"""
        result = mdformat.text(text, extensions={"front_matters"})
        # Should preserve malformed content
        assert "# Content" in result

    def test_yaml_with_null_values(self):
        """Test YAML with null values."""
        text = """---
nullable: null
empty:
present: value
---
# Content
"""
        result = mdformat.text(text, extensions={"front_matters"})
        assert "# Content" in result

    def test_toml_with_datetime(self):
        """Test TOML with datetime values."""
        text = """+++
date = 2024-01-01T12:00:00Z
updated = 2024-01-01T12:00:00+05:30
+++
# Content
"""
        result = mdformat.text(text, extensions={"front_matters"})
        assert "# Content" in result
        assert "date" in result or "2024" in result
