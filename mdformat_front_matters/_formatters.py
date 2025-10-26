"""Lazy-loaded formatters for different front matter formats."""

from __future__ import annotations

import json
import sys
import types
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

from ._helpers import DuplicateKeyError

T = TypeVar("T")


class YAMLFormatter:
    """Lazy-loaded YAML formatter using PyYAML."""

    _yaml_module: types.ModuleType | None = None
    _dumper_class: type | None = None

    @classmethod
    def format(cls, content: str) -> str:
        """Format YAML content.

        Args:
            content: Raw YAML string to format.

        Returns:
            Formatted YAML string.

        """
        if cls._yaml_module is None or cls._dumper_class is None:
            cls._load_formatter()

        # First, check for duplicate keys
        cls._check_duplicate_keys(content)

        try:
            assert cls._yaml_module is not None
            # Parse and re-dump to format
            parsed = cls._yaml_module.safe_load(content)

            # Handle empty/null content
            if parsed is None or (isinstance(parsed, str) and not parsed.strip()):
                return "null"

            # Dump with specific formatting options for consistency
            # Note: sort_keys=False to preserve original key order (YAML is not sorted)
            assert cls._dumper_class is not None
            formatted = cls._yaml_module.dump(
                parsed,
                Dumper=cls._dumper_class,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                explicit_start=False,
                explicit_end=False,
                width=80,  # Wrap lines at 80 characters for readability
            )

            # Remove YAML document end marker (...) if present
            if formatted.endswith("\n...\n"):
                formatted = formatted[:-5]
            elif formatted.endswith("\n..."):
                formatted = formatted[:-4]

            # Normalize datetime formatting to use T instead of space
            formatted = cls._normalize_datetimes(formatted)

            # Convert | to |- for block scalars that should strip trailing newlines
            # This is a workaround for PyYAML not supporting |- directly
            formatted = cls._fix_block_scalar_chomping(formatted)

            # Remove trailing newline if present
            formatted = formatted.rstrip("\n")
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            return formatted

    @classmethod
    def _check_duplicate_keys(cls, content: str) -> None:
        """Check for duplicate keys in YAML content.

        Args:
            content: Raw YAML string to check.

        Raises:
            DuplicateKeyError: If duplicate keys are found.

        """
        assert cls._yaml_module is not None

        class DuplicateKeysLoader(cls._yaml_module.SafeLoader):  # type: ignore[name-defined]
            """Custom YAML loader that detects duplicate keys."""

            def construct_mapping(
                self, node: Any, deep: bool = False,  # noqa: ANN401, FBT002
            ) -> dict[Any, Any]:
                """Override mapping construction to detect duplicates.

                Raises:
                    DuplicateKeyError: If duplicate keys are detected.

                """
                mapping = {}
                for key_node, value_node in node.value:
                    key = self.construct_object(key_node, deep=deep)
                    if key in mapping:
                        raise DuplicateKeyError(str(key), "yaml")
                    mapping[key] = self.construct_object(value_node, deep=deep)
                return mapping

        try:
            cls._yaml_module.load(content, Loader=DuplicateKeysLoader)
        except DuplicateKeyError:
            raise
        except Exception:  # noqa: S110
            # If YAML parsing fails for other reasons, let the formatter handle it
            pass

    @staticmethod
    def _fix_block_scalar_chomping(yaml_str: str) -> str:
        """Fix block scalar chomping indicators.

        PyYAML doesn't properly support |- for block scalars without trailing newlines.
        This method detects such cases and converts | to |-.

        Args:
            yaml_str: YAML string with block scalars.

        Returns:
            YAML string with corrected chomping indicators.

        """
        # Pattern: key: | followed by indented lines, ending with non-empty line
        # We need to replace | with |- if the last line has content (not just whitespace)
        # This is tricky because we need to look ahead to see the content

        # Simpler approach: detect `: |\n` followed by content that ends with
        # a line that isn't blank (before the next key or end of block)
        lines = yaml_str.split("\n")
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this line ends with ': |'
            if line.rstrip().endswith(": |"):
                # Look ahead to see if we need |-
                # Find the indentation level of the block
                base_indent = len(line) - len(line.lstrip())
                # Collect the block lines
                j = i + 1
                block_lines = []
                while j < len(lines):
                    next_line = lines[j]
                    # Check if this line is part of the block (more indented or empty)
                    if next_line.strip() == "" or len(next_line) - len(next_line.lstrip()) > base_indent:
                        block_lines.append(next_line)
                        j += 1
                    else:
                        break
                # Check if the last non-empty line should use |-
                # (i.e., the original content didn't have a trailing newline)
                # We added a newline, so the last line will be indented content
                non_empty_lines = [l for l in block_lines if l.strip()]
                if non_empty_lines and block_lines and block_lines[-1].strip() == "":
                    # Last line is empty, but there are non-empty lines before it
                    # This means we added a trailing newline - use |-
                    result_lines.append(line.replace(": |", ": |-", 1))
                else:
                    result_lines.append(line)
                result_lines.extend(block_lines)
                i = j
            else:
                result_lines.append(line)
                i += 1
        return "\n".join(result_lines)

    @staticmethod
    def _normalize_datetimes(yaml_str: str) -> str:
        """Normalize datetime formatting to use T instead of space.

        Args:
            yaml_str: YAML string with potential datetime values.

        Returns:
            YAML string with normalized datetime format.

        """
        import re  # noqa: PLC0415

        # Match datetime patterns like "2024-02-02 04:14:54"
        # and replace space with T
        pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})"
        return re.sub(pattern, r"\1T\2", yaml_str)

    @classmethod
    def _load_formatter(cls) -> None:
        """Lazy-load the PyYAML library."""
        import yaml  # type: ignore[import-untyped]  # noqa: PLC0415

        cls._yaml_module = yaml

        # Create custom Dumper that uses block scalars for multiline strings
        class BlockScalarDumper(yaml.SafeDumper):  # type: ignore[name-defined]
            """Custom YAML dumper that prefers block scalars for multiline strings."""

        def represent_str(dumper: yaml.SafeDumper, data: str) -> yaml.Node:  # type: ignore[name-defined]
            """Represent strings using block scalars for multiline content."""
            if "\n" in data:
                # Choose block scalar style based on content
                # Count internal newlines (excluding potential trailing newline)
                internal_newlines = data.rstrip("\n").count("\n")

                if internal_newlines == 0 and data.endswith("\n"):
                    # Single line with trailing newline - use folded style
                    style = ">"
                    use_data = data
                elif internal_newlines > 0 and not data.endswith("\n"):
                    # Multiple lines without trailing newline
                    # PyYAML won't use block scalars without trailing newline
                    # Workaround: add newline, use |, mark for post-processing
                    style = "|"
                    use_data = data + "\n"
                    node = dumper.represent_scalar("tag:yaml.org,2002:str", use_data, style=style)
                    # Store marker in node for post-processing
                    node.comment = ["STRIP"]  # type: ignore[attr-defined]
                    return node
                else:
                    # Multiple lines with trailing newline - use literal style
                    style = "|"
                    use_data = data
                return dumper.represent_scalar("tag:yaml.org,2002:str", use_data, style=style)
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        # Register for both str types
        BlockScalarDumper.add_representer(str, represent_str)
        cls._dumper_class = BlockScalarDumper


class TOMLFormatter:
    """Lazy-loaded TOML formatter using tomli/tomli-w."""

    _loads_fn: Callable[[str], dict[str, Any]] | None = None
    _dumps_fn: Callable[[dict[str, Any]], str] | None = None

    @classmethod
    def format(cls, content: str, sort_keys: bool = True) -> str:  # noqa: FBT002
        """Format TOML content.

        Args:
            content: Raw TOML string to format.
            sort_keys: Whether to sort keys alphabetically (default: True).

        Returns:
            Formatted TOML string.

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

        """
        if cls._loads_fn is None or cls._dumps_fn is None:
            cls._load_formatter()

        try:
            # Parse and re-dump to format
            assert cls._loads_fn is not None
            assert cls._dumps_fn is not None
            parsed = cls._loads_fn(content)
            if sort_keys:
                parsed = cls._sort_dict_recursive(parsed)
            formatted = cls._dumps_fn(parsed)
            # tomli-w uses space in datetimes, but TOML spec prefers T
            # Replace datetime spaces with T for better compatibility
            formatted = cls._normalize_datetimes(formatted)
        except Exception as e:
            # Check if this is a duplicate key error from tomli
            error_msg = str(e).lower()
            if (
                "cannot overwrite" in error_msg
                or "duplicate" in error_msg
                or "already exists" in error_msg
            ):
                # Cannot extract key name from tomli's error message
                raise DuplicateKeyError("unknown", "toml") from e
            # If formatting fails for other reasons, return original content
            return content
        else:
            # Remove trailing newline if present
            return formatted.rstrip("\n")

    @staticmethod
    def _sort_dict_recursive(data: T) -> T:
        """Recursively sort dictionaries by their keys.

        Args:
            data: Data structure to sort (can be dict, list, or other types).

        Returns:
            Sorted data structure with all nested dicts sorted by keys.

        """
        if isinstance(data, dict):
            return {
                k: TOMLFormatter._sort_dict_recursive(v)
                for k, v in sorted(data.items())
            }  # type: ignore[return-value]
        if isinstance(data, list):
            return [TOMLFormatter._sort_dict_recursive(item) for item in data]  # type: ignore[return-value]
        return data

    @staticmethod
    def _normalize_datetimes(toml_str: str) -> str:
        """Normalize datetime formatting to use T instead of space.

        Args:
            toml_str: TOML string with potential datetime values.

        Returns:
            TOML string with normalized datetime format.

        """
        import re  # noqa: PLC0415

        # Match datetime patterns like "2024-02-02 04:14:54"
        # and replace space with T
        pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})"
        return re.sub(pattern, r"\1T\2", toml_str)

    @classmethod
    def _load_formatter(cls) -> None:
        """Lazy-load the tomli/tomli-w libraries."""
        # Use tomllib for Python 3.11+, tomli for older versions
        if sys.version_info >= (3, 11):
            import tomllib  # noqa: PLC0415

            cls._loads_fn = tomllib.loads
        else:
            import tomli  # type: ignore[import-not-found]  # noqa: PLC0415

            cls._loads_fn = tomli.loads

        import tomli_w  # noqa: PLC0415

        cls._dumps_fn = tomli_w.dumps


class JSONFormatter:
    """JSON formatter using standard library."""

    @staticmethod
    def format(content: str, sort_keys: bool = True) -> str:  # noqa: FBT002
        """Format JSON content.

        Args:
            content: Raw JSON string to format.
            sort_keys: Whether to sort keys alphabetically (default: True).

        Returns:
            Formatted JSON string with 2-space indentation.

        Raises:
            DuplicateKeyError: If duplicate keys are detected.

        """
        def check_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            """Check for duplicate keys in object pairs.

            Args:
                pairs: List of key-value pairs from JSON object.

            Returns:
                Dictionary constructed from pairs.

            Raises:
                DuplicateKeyError: If duplicate keys are found.

            """
            seen_keys: set[str] = set()
            result = {}
            for key, value in pairs:
                if key in seen_keys:
                    raise DuplicateKeyError(key, "json")
                seen_keys.add(key)
                result[key] = value
            return result

        try:
            # Parse with duplicate key detection
            parsed = json.loads(content, object_pairs_hook=check_duplicates)
        except DuplicateKeyError:
            raise
        except Exception:
            # If formatting fails, return original content
            return content
        else:
            return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=sort_keys)
