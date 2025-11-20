"""Performance tests to ensure reasonable execution speed."""

from __future__ import annotations

import time

import pytest

import mdformat


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
    start = time.time()
    result = mdformat.text(large_yaml_document, extensions={"front_matters"})
    elapsed = time.time() - start

    assert result is not None
    assert "# Content" in result
    assert "data:" in result
    # Should format in under 2 seconds
    assert elapsed < 2.0, f"Formatting took {elapsed:.2f}s, expected < 2.0s"


def test_large_toml_performance(large_toml_document):
    """Test that large TOML documents are formatted in reasonable time."""
    start = time.time()
    result = mdformat.text(large_toml_document, extensions={"front_matters"})
    elapsed = time.time() - start

    assert result is not None
    assert "# Content" in result
    # Should format in under 2 seconds
    assert elapsed < 2.0, f"Formatting took {elapsed:.2f}s, expected < 2.0s"


def test_deeply_nested_yaml_performance(deeply_nested_yaml):
    """Test that deeply nested YAML is formatted in reasonable time."""
    start = time.time()
    result = mdformat.text(deeply_nested_yaml, extensions={"front_matters"})
    elapsed = time.time() - start

    assert result is not None
    assert "# Content" in result
    # Should format in under 1 second
    assert elapsed < 1.0, f"Formatting took {elapsed:.2f}s, expected < 1.0s"


def test_multiple_documents_performance():
    """Test formatting multiple documents in sequence."""
    documents = [
        """---
title: Document {i}
date: 2024-01-{i:02d}
tags:
  - tag1
  - tag2
---
# Content {i}
""".format(
            i=i
        )
        for i in range(1, 101)
    ]

    start = time.time()
    for doc in documents:
        result = mdformat.text(doc, extensions={"front_matters"})
        assert result is not None
    elapsed = time.time() - start

    # 100 documents should format in under 3 seconds
    assert elapsed < 3.0, f"Formatting 100 docs took {elapsed:.2f}s, expected < 3.0s"


@pytest.mark.parametrize("count", [10, 100, 500])
def test_scalability_with_array_size(count):
    """Test that performance scales reasonably with array size."""
    items = ", ".join(f'"item_{i}"' for i in range(count))
    text = f"""---
items: [{items}]
---
# Content
"""

    start = time.time()
    result = mdformat.text(text, extensions={"front_matters"})
    elapsed = time.time() - start

    assert result is not None
    # Should complete in under 1 second even for 500 items
    assert elapsed < 1.0, f"Formatting {count} items took {elapsed:.2f}s"


def test_json_performance():
    """Test JSON front matter performance."""
    # Create large JSON object
    entries = ",\n".join(f'    "key_{i}": "value_{i}"' for i in range(500))
    text = f"""{{
{entries}
}}
# Content
"""

    start = time.time()
    result = mdformat.text(text, extensions={"front_matters"})
    elapsed = time.time() - start

    assert result is not None
    assert "# Content" in result
    # Should format in under 1 second
    assert elapsed < 1.0, f"JSON formatting took {elapsed:.2f}s, expected < 1.0s"


def test_empty_document_performance():
    """Test that empty documents are handled efficiently."""
    text = "# Just a heading\n\nNo front matter here.\n"

    start = time.time()
    for _ in range(1000):
        result = mdformat.text(text, extensions={"front_matters"})
        assert result is not None
    elapsed = time.time() - start

    # 1000 iterations should complete in under 2 seconds
    assert elapsed < 2.0, f"1000 iterations took {elapsed:.2f}s, expected < 2.0s"
