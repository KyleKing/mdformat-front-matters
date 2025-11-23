"""Performance tests to ensure reasonable execution speed."""

from __future__ import annotations

import time

import mdformat
import pytest
from typing_extensions import Self


class Timer:
    """Context manager for timing operations with assertion method."""

    def __enter__(self) -> Self:
        """Start timer."""
        self.start = time.time()
        return self

    def __exit__(self, *args) -> None:
        """End timer."""
        self.elapsed = time.time() - self.start

    def assert_(self, max_time: float) -> None:
        """Assert that elapsed time is less than max_time."""
        assert self.elapsed < max_time, (
            f"Operation took {self.elapsed:.2f}s, expected < {max_time}s"
        )


@pytest.fixture
def large_yaml_document():
    """Generate a large YAML front matter document."""
    # Create 1000 key-value pairs
    entries = "\n".join(f"  key_{i}: value_{i}" for i in range(1000))
    return f"""---
data:
{entries}
---
# Content

This is some markdown content with multiple paragraphs.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Section 2

More content here.
"""


@pytest.fixture
def large_toml_document():
    """Generate a large TOML front matter document."""
    # Create 1000 key-value pairs
    entries = "\n".join(f'key_{i} = "value_{i}"' for i in range(1000))
    return f"""+++
{entries}
+++
# Content

This is some markdown content.
"""


@pytest.fixture
def deeply_nested_yaml():
    """Generate a deeply nested YAML structure."""
    # Create 100 levels of nesting
    nesting = "level:\n  " * 100 + "value: test"
    return f"""---
{nesting}
---
# Content
"""


def test_large_yaml_performance(large_yaml_document):
    """Test that large YAML documents are formatted in reasonable time."""
    with Timer() as timer:
        result = mdformat.text(large_yaml_document, extensions={"front_matters"})

    assert result is not None
    assert "# Content" in result
    assert "data:" in result
    # Should format in under 2 seconds
    timer.assert_(2.0)  # noqa: PT009


def test_large_toml_performance(large_toml_document):
    """Test that large TOML documents are formatted in reasonable time."""
    with Timer() as timer:
        result = mdformat.text(large_toml_document, extensions={"front_matters"})

    assert result is not None
    assert "# Content" in result
    # Should format in under 2 seconds
    timer.assert_(2.0)  # noqa: PT009


def test_deeply_nested_yaml_performance(deeply_nested_yaml):
    """Test that deeply nested YAML is formatted in reasonable time."""
    with Timer() as timer:
        result = mdformat.text(deeply_nested_yaml, extensions={"front_matters"})

    assert result is not None
    assert "# Content" in result
    # Should format in under 1 second
    timer.assert_(1.0)  # noqa: PT009


def test_multiple_documents_performance():
    """Test formatting multiple documents in sequence."""
    documents = [
        f"""---
title: Document {i}
date: 2024-01-{i:02d}
tags:
  - tag1
  - tag2
---
# Content {i}
"""
        for i in range(1, 101)
    ]

    with Timer() as timer:
        for doc in documents:
            result = mdformat.text(doc, extensions={"front_matters"})
            assert result is not None

    # 100 documents should format in under 3 seconds
    timer.assert_(3.0)  # noqa: PT009


@pytest.mark.parametrize("count", [10, 100, 500])
def test_scalability_with_array_size(count):
    """Test that performance scales reasonably with array size."""
    items = ", ".join(f'"item_{i}"' for i in range(count))
    text = f"""---
items: [{items}]
---
# Content
"""

    with Timer() as timer:
        result = mdformat.text(text, extensions={"front_matters"})

    assert result is not None
    # Should complete in under 1 second even for 500 items
    timer.assert_(1.0)  # noqa: PT009


def test_json_performance():
    # Create large JSON object
    entries = ",\n".join(f'    "key_{i}": "value_{i}"' for i in range(500))
    text = f"""{{
{entries}
}}
# Content
"""

    with Timer() as timer:
        result = mdformat.text(text, extensions={"front_matters"})

    assert result is not None
    assert "# Content" in result
    # Should format in under 1 second
    timer.assert_(1.0)  # noqa: PT009


def test_empty_document_performance():
    text = "# Just a heading\n\nNo front matter here.\n"

    with Timer() as timer:
        for _ in range(1000):
            result = mdformat.text(text, extensions={"front_matters"})
            assert result is not None

    # 1000 iterations should complete in under 2 seconds
    timer.assert_(2.0)  # noqa: PT009
