"""Tests for helper functions."""

from __future__ import annotations

import pytest

from mdformat_front_matters._helpers import get_conf


@pytest.fixture
def empty_options():
    """Options with no configuration."""
    return {
        "mdformat": {},
    }


@pytest.fixture
def api_options():
    """Options with API-level configuration."""
    return {
        "mdformat": {
            "test_key": "api_value",
            "plugin": {},
        },
    }


@pytest.fixture
def plugin_options():
    """Options with plugin-level configuration."""
    return {
        "mdformat": {
            "plugin": {
                "front_matters": {
                    "test_key": "plugin_value",
                },
            },
        },
    }


@pytest.fixture
def both_options():
    """Options with both API and plugin configuration."""
    return {
        "mdformat": {
            "test_key": "api_value",
            "plugin": {
                "front_matters": {
                    "test_key": "plugin_value",
                },
            },
        },
    }


def test_get_conf_from_api(api_options):
    """Test retrieving configuration from API."""
    assert get_conf(api_options, "test_key") == "api_value"


def test_get_conf_from_plugin(plugin_options):
    """Test retrieving configuration from plugin settings."""
    assert get_conf(plugin_options, "test_key") == "plugin_value"


def test_get_conf_api_precedence(both_options):
    """Test that API configuration takes precedence over plugin configuration."""
    assert get_conf(both_options, "test_key") == "api_value"


def test_get_conf_missing_key(plugin_options):
    """Test that missing keys return None."""
    assert get_conf(plugin_options, "nonexistent_key") is None


def test_get_conf_missing_plugin_section(empty_options):
    """Test handling of missing plugin section."""
    assert get_conf(empty_options, "test_key") is None


def test_get_conf_missing_front_matters_section():
    """Test handling of missing front_matters section."""
    options = {
        "mdformat": {
            "plugin": {},
        },
    }
    assert get_conf(options, "test_key") is None


@pytest.mark.parametrize(
    ("key", "value", "expected_type"),
    [
        ("strict", True, bool),
        ("max_depth", 10, int),
        ("format", "yaml", str),
        ("enabled", False, bool),
        ("indent", 0, int),
    ],
)
def test_get_conf_value_types(key, value, expected_type):
    """Test retrieving various configuration value types."""
    options = {
        "mdformat": {
            "plugin": {
                "front_matters": {
                    key: value,
                },
            },
        },
    }
    result = get_conf(options, key)
    assert result == value
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    ("value", "description"),
    [
        (False, "False boolean value"),
        (0, "Zero integer value"),
        ("", "Empty string value"),
    ],
)
def test_get_conf_falsy_values(value, description):
    """Test that falsy values are returned correctly (not confused with None)."""
    options = {
        "mdformat": {
            "plugin": {
                "front_matters": {
                    "test_key": value,
                },
            },
        },
    }
    result = get_conf(options, "test_key")
    assert result == value
    assert result is not None
