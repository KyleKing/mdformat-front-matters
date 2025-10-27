"""Tests for duplicate key detection in front matter."""

from __future__ import annotations

import mdformat
import pytest

from mdformat_front_matters._formatters import (
    JSONFormatter,
    TOMLFormatter,
    YAMLFormatter,
)
from mdformat_front_matters._helpers import DuplicateKeyError


class TestYAMLDuplicateKeys:
    """Test YAML duplicate key detection."""

    def test_yaml_duplicate_keys_simple(self) -> None:
        """Test that duplicate keys in YAML raise DuplicateKeyError."""
        yaml_content = """key: value1
key: value2"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            YAMLFormatter.format(yaml_content)
        assert exc_info.value.key == "key"
        assert exc_info.value.format_type == "yaml"
        assert "Duplicate key 'key' found in YAML front matter" in str(exc_info.value)

    def test_yaml_duplicate_keys_different_values(self) -> None:
        """Test that duplicate keys with different values raise error."""
        yaml_content = """stuff: stuff1
other: value
stuff: stuff2"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            YAMLFormatter.format(yaml_content)
        assert exc_info.value.key == "stuff"
        assert exc_info.value.format_type == "yaml"

    def test_yaml_no_duplicate_keys(self) -> None:
        """Test that unique keys do not raise error."""
        yaml_content = """key1: value1
key2: value2
key3: value3"""
        # Should not raise
        result = YAMLFormatter.format(yaml_content)
        assert "key1" in result
        assert "key2" in result
        assert "key3" in result

    def test_yaml_nested_duplicate_keys(self) -> None:
        """Test that duplicate keys in nested structures raise error."""
        yaml_content = """outer:
  inner: value1
  inner: value2"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            YAMLFormatter.format(yaml_content)
        assert exc_info.value.key == "inner"


class TestJSONDuplicateKeys:
    """Test JSON duplicate key detection."""

    def test_json_duplicate_keys_simple(self) -> None:
        """Test that duplicate keys in JSON raise DuplicateKeyError."""
        json_content = """{"key": "value1", "key": "value2"}"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            JSONFormatter.format(json_content)
        assert exc_info.value.key == "key"
        assert exc_info.value.format_type == "json"
        assert "Duplicate key 'key' found in JSON front matter" in str(exc_info.value)

    def test_json_duplicate_keys_different_values(self) -> None:
        """Test that duplicate keys with different values raise error."""
        json_content = """{"stuff": "stuff1", "other": "value", "stuff": "stuff2"}"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            JSONFormatter.format(json_content)
        assert exc_info.value.key == "stuff"
        assert exc_info.value.format_type == "json"

    def test_json_no_duplicate_keys(self) -> None:
        """Test that unique keys do not raise error."""
        json_content = """{"key1": "value1", "key2": "value2", "key3": "value3"}"""
        # Should not raise
        result = JSONFormatter.format(json_content)
        assert "key1" in result
        assert "key2" in result
        assert "key3" in result

    def test_json_nested_duplicate_keys(self) -> None:
        """Test that duplicate keys in nested structures raise error."""
        json_content = """{"outer": {"inner": "value1", "inner": "value2"}}"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            JSONFormatter.format(json_content)
        assert exc_info.value.key == "inner"


class TestTOMLDuplicateKeys:
    """Test TOML duplicate key detection."""

    def test_toml_duplicate_keys_simple(self) -> None:
        """Test that duplicate keys in TOML raise error (via tomli)."""
        toml_content = """key = "value1"
key = "value2"
"""
        # tomli raises TOMLDecodeError, which we convert to DuplicateKeyError
        with pytest.raises(DuplicateKeyError) as exc_info:
            TOMLFormatter.format(toml_content)
        assert exc_info.value.format_type == "toml"
        assert "Duplicate key" in str(exc_info.value)

    def test_toml_no_duplicate_keys(self) -> None:
        """Test that unique keys do not raise error."""
        toml_content = """key1 = "value1"
key2 = "value2"
key3 = "value3"
"""
        # Should not raise
        result = TOMLFormatter.format(toml_content)
        assert "key1" in result
        assert "key2" in result
        assert "key3" in result


class TestMdformatIntegration:
    """Test that duplicate keys are caught at the mdformat level."""

    def test_mdformat_yaml_duplicate_keys(self) -> None:
        """Test that mdformat.text() raises on YAML duplicate keys."""
        text = """---
title: First
title: Second
---

# Document"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            mdformat.text(text, extensions={"front_matters"})
        assert exc_info.value.key == "title"
        assert exc_info.value.format_type == "yaml"

    def test_mdformat_json_duplicate_keys(self) -> None:
        """Test that mdformat.text() raises on JSON duplicate keys."""
        text = """{
  "title": "First",
  "title": "Second"
}

# Document"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            mdformat.text(text, extensions={"front_matters"})
        assert exc_info.value.key == "title"
        assert exc_info.value.format_type == "json"

    def test_mdformat_toml_duplicate_keys(self) -> None:
        """Test that mdformat.text() raises on TOML duplicate keys."""
        text = """+++
title = "First"
title = "Second"
+++

# Document"""
        with pytest.raises(DuplicateKeyError) as exc_info:
            mdformat.text(text, extensions={"front_matters"})
        assert exc_info.value.format_type == "toml"
