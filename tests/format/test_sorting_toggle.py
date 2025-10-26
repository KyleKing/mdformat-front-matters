"""Tests for sorting toggle functionality."""

from __future__ import annotations

import mdformat


class TestSortingToggle:
    """Test that the --no-sort-keys flag works correctly."""

    def test_toml_sorting_enabled_by_default(self) -> None:
        """Test that TOML keys are sorted by default."""
        text = """+++
title = "Example"
date = 2024-02-02T04:14:54-08:00
draft = false
+++

# Content"""
        result = mdformat.text(text, extensions={"front_matters"})
        # Keys should be sorted alphabetically: date, draft, title
        expected = 'date = 2024-02-02T04:14:54-08:00\ndraft = false\ntitle = "Example"'
        assert expected in result

    def test_toml_sorting_disabled(self) -> None:
        """Test that TOML keys are not sorted when --no-sort-keys is used."""
        text = """+++
title = "Example"
date = 2024-02-02T04:14:54-08:00
draft = false
+++

# Content"""
        result = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"no_sort_keys": True},
        )
        # Keys should remain in original order: title, date, draft
        expected = 'title = "Example"\ndate = 2024-02-02T04:14:54-08:00\ndraft = false'
        assert expected in result

    def test_json_sorting_enabled_by_default(self) -> None:
        """Test that JSON keys are sorted by default."""
        text = """{
  "title": "Example",
  "date": "2024-02-02",
  "draft": false
}

# Content"""
        result = mdformat.text(text, extensions={"front_matters"})
        # Keys should be sorted alphabetically: date, draft, title
        expected = '"date": "2024-02-02",\n  "draft": false,\n  "title": "Example"'
        assert expected in result

    def test_json_sorting_disabled(self) -> None:
        """Test that JSON keys are not sorted when --no-sort-keys is used."""
        text = """{
  "title": "Example",
  "date": "2024-02-02",
  "draft": false
}

# Content"""
        result = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"no_sort_keys": True},
        )
        # Keys should remain in original order: title, date, draft
        expected = '"title": "Example",\n  "date": "2024-02-02",\n  "draft": false'
        assert expected in result

    def test_yaml_unaffected_by_sorting_toggle(self) -> None:
        """Test that YAML is unaffected by the sorting toggle."""
        text = """---
title: Example
date: 2024-02-02
draft: false
---

# Content"""
        # With sorting enabled (default)
        result_sorted = mdformat.text(text, extensions={"front_matters"})
        # With sorting disabled
        result_unsorted = mdformat.text(
            text,
            extensions={"front_matters"},
            options={"no_sort_keys": True},
        )
        # Both should be the same since YAML doesn't get sorted
        assert result_sorted == result_unsorted
        assert "title: Example\ndate: 2024-02-02\ndraft: false" in result_sorted
