"""Test key sorting functionality for front matter."""

from __future__ import annotations

import mdformat
import pytest


class TestYAMLSorting:
    """Test YAML key sorting."""

    def test_yaml_unsorted_default(self):
        """Test that YAML keys are not sorted by default."""
        text = """\
---
zebra: last
apple: first
middle: second
---
# Heading
"""
        expected = """\
---
zebra: last
apple: first
middle: second
---

# Heading
"""
        output = mdformat.text(text, extensions={"front_matters"})
        assert output == expected

    def test_yaml_sorted_with_flag(self):
        """Test that YAML keys are sorted when flag is enabled."""
        text = """\
---
zebra: last
apple: first
middle: second
---
# Heading
"""
        expected = """\
---
apple: first
middle: second
zebra: last
---

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected

    def test_yaml_nested_sorted(self):
        """Test that nested YAML keys are also sorted."""
        text = """\
---
zebra: last
nested:
  zoo: z
  alpha: a
apple: first
---
# Heading
"""
        expected = """\
---
apple: first
nested:
  alpha: a
  zoo: z
zebra: last
---

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected


class TestTOMLSorting:
    """Test TOML key sorting."""

    def test_toml_unsorted_default(self):
        """Test that TOML keys are not sorted by default."""
        text = """\
+++
zebra = "last"
apple = "first"
middle = "second"
+++
# Heading
"""
        expected = """\
+++
zebra = "last"
apple = "first"
middle = "second"
+++

# Heading
"""
        output = mdformat.text(text, extensions={"front_matters"})
        assert output == expected

    def test_toml_sorted_with_flag(self):
        """Test that TOML keys are sorted when flag is enabled."""
        text = """\
+++
zebra = "last"
apple = "first"
middle = "second"
+++
# Heading
"""
        expected = """\
+++
apple = "first"
middle = "second"
zebra = "last"
+++

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected

    def test_toml_nested_tables_sorted(self):
        """Test that nested TOML tables are also sorted."""
        text = """\
+++
zebra = "last"
apple = "first"

[nested]
zoo = "z"
alpha = "a"
+++
# Heading
"""
        expected = """\
+++
apple = "first"
zebra = "last"

[nested]
alpha = "a"
zoo = "z"
+++

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected


class TestJSONSorting:
    """Test JSON key sorting."""

    def test_json_unsorted_default(self):
        """Test that JSON keys are not sorted by default."""
        text = """\
{
"zebra": "last",
"apple": "first",
"middle": "second"
}
# Heading
"""
        expected = """\
{
  "zebra": "last",
  "apple": "first",
  "middle": "second"
}

# Heading
"""
        output = mdformat.text(text, extensions={"front_matters"})
        assert output == expected

    def test_json_sorted_with_flag(self):
        """Test that JSON keys are sorted when flag is enabled."""
        text = """\
{
"zebra": "last",
"apple": "first",
"middle": "second"
}
# Heading
"""
        expected = """\
{
  "apple": "first",
  "middle": "second",
  "zebra": "last"
}

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected

    def test_json_nested_sorted(self):
        """Test that nested JSON objects are also sorted."""
        text = """\
{
"zebra": "last",
"nested": {"zoo": "z", "alpha": "a"},
"apple": "first"
}
# Heading
"""
        expected = """\
{
  "apple": "first",
  "nested": {
    "alpha": "a",
    "zoo": "z"
  },
  "zebra": "last"
}

# Heading
"""
        output = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"front_matters_sort_keys": True},
        )
        assert output == expected
