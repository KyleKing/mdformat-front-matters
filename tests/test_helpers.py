"""Tests for helper functions."""

from __future__ import annotations

import pytest

from mdformat_front_matters._helpers import get_conf


class TestGetConf:
    """Tests for the get_conf function."""

    def test_get_conf_from_api(self):
        """Test retrieving configuration from API."""
        options = {
            "mdformat": {
                "test_key": "api_value",
                "plugin": {},
            },
        }
        assert get_conf(options, "test_key") == "api_value"

    def test_get_conf_from_plugin(self):
        """Test retrieving configuration from plugin settings."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "test_key": "plugin_value",
                    },
                },
            },
        }
        assert get_conf(options, "test_key") == "plugin_value"

    def test_get_conf_api_precedence(self):
        """Test that API configuration takes precedence over plugin configuration."""
        options = {
            "mdformat": {
                "test_key": "api_value",
                "plugin": {
                    "front_matters": {
                        "test_key": "plugin_value",
                    },
                },
            },
        }
        assert get_conf(options, "test_key") == "api_value"

    def test_get_conf_missing_key(self):
        """Test that missing keys return None."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {},
                },
            },
        }
        assert get_conf(options, "nonexistent_key") is None

    def test_get_conf_missing_plugin_section(self):
        """Test handling of missing plugin section."""
        options = {
            "mdformat": {},
        }
        assert get_conf(options, "test_key") is None

    def test_get_conf_missing_front_matters_section(self):
        """Test handling of missing front_matters section."""
        options = {
            "mdformat": {
                "plugin": {},
            },
        }
        assert get_conf(options, "test_key") is None

    def test_get_conf_boolean_value(self):
        """Test retrieving boolean configuration values."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "strict": True,
                    },
                },
            },
        }
        assert get_conf(options, "strict") is True

    def test_get_conf_integer_value(self):
        """Test retrieving integer configuration values."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "max_depth": 10,
                    },
                },
            },
        }
        assert get_conf(options, "max_depth") == 10

    def test_get_conf_string_value(self):
        """Test retrieving string configuration values."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "format": "yaml",
                    },
                },
            },
        }
        assert get_conf(options, "format") == "yaml"

    def test_get_conf_false_value(self):
        """Test that False boolean value is returned correctly."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "enabled": False,
                    },
                },
            },
        }
        assert get_conf(options, "enabled") is False

    def test_get_conf_zero_value(self):
        """Test that zero integer value is returned correctly."""
        options = {
            "mdformat": {
                "plugin": {
                    "front_matters": {
                        "indent": 0,
                    },
                },
            },
        }
        assert get_conf(options, "indent") == 0
