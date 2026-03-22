"""Front matter formatters for YAML, TOML, and JSON."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
from typing import Any

import toml  # type: ignore[import-untyped]
from mdformat.renderer import LOGGER
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.representer import RoundTripRepresenter as _RoundTripRepresenter
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, SingleQuotedScalarString

SPECIAL_YAML_CHARS = {
    ":",
    "{",
    "}",
    "[",
    "]",
    ",",
    "&",
    "*",
    "#",
    "?",
    "|",
    "-",
    "<",
    ">",
    "=",
    "!",
    "%",
    "@",
    "`",
    '"',
    "'",
}
"""These characters require quoting: : { } [ ] , & * # ? | - < > = ! % @ `."""

_YAML11_TRUE_WORDS: frozenset[str] = frozenset({"y", "Y", "yes", "Yes", "YES", "on", "On", "ON"})
_YAML11_FALSE_WORDS: frozenset[str] = frozenset({"n", "N", "no", "No", "NO", "off", "Off", "OFF"})


class _NullNormalizingRepresenter(_RoundTripRepresenter):
    """RoundTripRepresenter that normalizes null values and strips quote styles.

    - ``None`` always outputs as ``null`` (not ``~``).
    - ``SingleQuotedScalarString`` / ``DoubleQuotedScalarString`` are output as
      plain scalars, stripping the original quote style. This is needed when the
      loader used ``preserve_quotes=True`` (e.g. for YAML 1.1 boolean detection)
      but the dumper should not honour those preserved styles.
      ``LiteralScalarString`` / ``FoldedScalarString`` are intentionally excluded
      so block scalar styles (``|``, ``>``) are always preserved.
    """


def _represent_as_plain_str(dumper: _NullNormalizingRepresenter, data: object) -> Any:
    return dumper.represent_str(str.__new__(str, data))


_NullNormalizingRepresenter.add_representer(
    type(None),
    lambda d, _: d.represent_scalar("tag:yaml.org,2002:null", "null"),
)
_NullNormalizingRepresenter.add_representer(SingleQuotedScalarString, _represent_as_plain_str)
_NullNormalizingRepresenter.add_representer(DoubleQuotedScalarString, _represent_as_plain_str)


class _RoundTripYAMLHandler:
    """Custom YAML handler for round-trip formatting with ruamel.yaml.

    Preserves unicode characters (including emojis), inline and block comments,
    and optionally the original quote style of string scalars (single-quoted,
    double-quoted, literal block ``|``, folded block ``>``).

    ruamel.yaml's constructor wraps quoted scalars in ``SingleQuotedScalarString``
    or ``DoubleQuotedScalarString`` when ``preserve_quotes=True``, and wraps
    block scalars in ``LiteralScalarString`` / ``FoldedScalarString`` regardless.
    See: https://sourceforge.net/p/ruamel-yaml/code/ci/default/tree/constructor.py#l985

    The ``normalize_mode`` kwarg controls normalization: ``"none"`` preserves
    everything, ``"minimal"`` strips unnecessary quotes and normalizes null/booleans,
    ``"1.2"`` additionally upgrades YAML 1.1 boolean words to ``true``/``false``.
    """

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """Export metadata as YAML, preserving unicode, comments, and optionally quotes.

        Args:
            metadata: Dictionary to export as YAML.
            **kwargs: Additional arguments. Recognized keys:
                sort_keys: Whether to sort keys alphabetically (default ``True``).
                normalize_mode: Normalization level — ``"none"`` preserves everything,
                    ``"minimal"`` strips unnecessary quotes and normalizes null/booleans,
                    ``"1.2"`` additionally upgrades YAML 1.1 boolean words to
                    ``true``/``false``. Defaults to ``"none"``.

        Returns:
            YAML string with preserved unicode characters and comments.
        """
        sort_keys = kwargs.pop("sort_keys", True)
        normalize_mode = str(kwargs.pop("normalize_mode", "none"))

        yaml = YAML()
        if normalize_mode == "none":
            yaml.preserve_quotes = True
        else:
            yaml.Representer = _NullNormalizingRepresenter
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        yaml.width = sys.maxsize
        yaml.indent(mapping=2, sequence=4, offset=2)

        if sort_keys:
            self._sort_mappings_in_place(metadata)

        if normalize_mode == "1.2":
            self._upgrade_yaml11_booleans(metadata)

        stream = StringIO()
        yaml.dump(metadata, stream)
        return stream.getvalue().strip()

    def _sort_mappings_in_place(
        self, data: CommentedMap | CommentedSeq | dict[str, object] | list[object]
    ) -> None:
        """Recursively sort dictionary keys in-place while preserving comments.

        This uses the .insert() method of CommentedMap to preserve end-of-line
        comments. The .pop() method doesn't delete comments, and .insert()
        re-associates them with the key.

        Based on: https://stackoverflow.com/a/51387713/3219667

        Args:
            data: Dictionary or list to sort in-place.
        """
        if isinstance(data, list):
            for elem in data:
                if isinstance(elem, (dict, list)):
                    self._sort_mappings_in_place(elem)
            return
        # Sort in reverse order and insert at position 0 to get ascending order
        for key in sorted(data, reverse=True):
            value = data.pop(key)
            if isinstance(value, (dict, list)):
                self._sort_mappings_in_place(value)
            data.insert(0, key, value)  # type: ignore[union-attr]

    def _upgrade_yaml11_booleans(
        self, data: CommentedMap | CommentedSeq | dict[str, object] | list[object]
    ) -> None:
        """Recursively convert unquoted YAML 1.1 boolean words to Python booleans.

        Only plain str values are converted — SingleQuotedScalarString and
        DoubleQuotedScalarString (loaded when preserve_quotes=True) are left as-is,
        since they represent intentional string values, not YAML 1.1 booleans.
        """
        if isinstance(data, dict):
            for key in data:
                value = data[key]
                if isinstance(value, str) and not isinstance(
                    value, (SingleQuotedScalarString, DoubleQuotedScalarString)
                ):
                    if value in _YAML11_TRUE_WORDS:
                        data[key] = True
                    elif value in _YAML11_FALSE_WORDS:
                        data[key] = False
                elif isinstance(value, (dict, list)):
                    self._upgrade_yaml11_booleans(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and not isinstance(
                    item, (SingleQuotedScalarString, DoubleQuotedScalarString)
                ):
                    if item in _YAML11_TRUE_WORDS:
                        data[i] = True  # type: ignore[index]
                    elif item in _YAML11_FALSE_WORDS:
                        data[i] = False  # type: ignore[index]
                elif isinstance(item, (dict, list)):
                    self._upgrade_yaml11_booleans(item)


class _SortingTOMLHandler:
    """Custom TOML handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:  # noqa: PLR6301
        """Export metadata as TOML with optional key sorting.

        Args:
            metadata: Dictionary to export as TOML.
            **kwargs: Additional arguments. Recognized keys:
                sort_keys: Whether to sort keys alphabetically (default ``True``).
                normalize_mode: Accepted for API consistency; TOML output is always
                    normalized regardless of this value.

        Returns:
            TOML string.
        """
        sort_keys_val = kwargs.pop("sort_keys", True)
        kwargs.pop("normalize_mode", None)
        sort_keys = bool(sort_keys_val) if sort_keys_val is not None else True
        if sort_keys:
            metadata = dict(sorted(metadata.items()))
        return toml.dumps(metadata)


class _SortingJSONHandler:
    """Custom JSON handler that supports key sorting."""

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:  # noqa: PLR6301
        """Export metadata as JSON with optional key sorting.

        Args:
            metadata: Dictionary to export as JSON.
            **kwargs: Additional arguments. Recognized keys:
                sort_keys: Whether to sort keys alphabetically (default ``True``).
                normalize_mode: Accepted for API consistency; JSON output is always
                    normalized regardless of this value.

        Returns:
            JSON string.
        """
        sort_keys_val = kwargs.pop("sort_keys", True)
        kwargs.pop("normalize_mode", None)
        sort_keys = bool(sort_keys_val) if sort_keys_val is not None else True
        return json.dumps(metadata, indent=4, sort_keys=sort_keys)


def _normalize_toml_output(content: str) -> str:
    """Normalize TOML output.

    Removes extra blank lines and trailing commas added by the TOML library.

    Args:
        content: TOML content to normalize.

    Returns:
        Normalized TOML content.
    """
    # Remove blank lines before section headers like [section]
    # but NOT array tables [[section]] - they should keep blank lines
    content = re.sub(r"\n\n+(\[(?!\[))", r"\n\1", content)

    # Remove trailing commas in arrays - handle both ,] and , ]
    # This handles: ["a", "b",] and ["a", "b", ] formats
    content = re.sub(r",\s*]", "]", content)

    # NOTE: We do NOT normalize array spacing (e.g., [ "item" -> ["item"])
    # because regex-based approach would corrupt bracket spacing inside strings.
    # Example: description = "[ spaced ]" would incorrectly become "[spaced]"

    # Remove blank line before closing (if present)
    return re.sub(r"\n\n+$", "\n", content)


def _strip_delimiters(formatted: str, delimiter: str) -> str:
    """Strip delimiters from formatted front matter.

    Args:
        formatted: Formatted front matter with delimiters.
        delimiter: The delimiter string (e.g., '---' or '+++').

    Returns:
        Front matter with delimiters removed and trailing newlines stripped.

    """
    formatted = formatted.removeprefix(f"{delimiter}\n")

    # Remove trailing delimiter with or without final newline
    end_with_nl = f"\n{delimiter}\n"
    end_no_nl = f"\n{delimiter}"

    if formatted.endswith(end_with_nl):
        return formatted[: -len(end_with_nl)].rstrip("\n")
    if formatted.endswith(end_no_nl):
        return formatted[: -len(end_no_nl)].rstrip("\n")
    return formatted.rstrip("\n")


class FormatError(Exception):
    """Exception raised when formatting fails and original content should be returned."""

    def __init__(self, content: str) -> None:
        """Initialize with original content to return.

        Args:
            content: Original content to return on formatting failure.
        """
        super().__init__()
        self.content = content


@contextmanager
def _handle_format_errors(
    content: str,
    format_type: str,
    *,
    strict: bool,
) -> Generator[None, None, None]:
    """Handle errors during front matter formatting.

    Args:
        content: Original content to return if formatting fails.
        format_type: Type of format being processed (e.g., 'YAML', 'TOML').
        strict: If True, raise exceptions instead of preserving original.

    Yields:
        None

    Raises:
        FormatError: When formatting fails in non-strict mode (contains original content).
        ValueError: Re-raised in strict mode from parsing/validation failures.
        TypeError: Re-raised in strict mode from invalid content types.
        AttributeError: Re-raised in strict mode from invalid content structure.
    """
    try:
        yield
    except (ValueError, TypeError, AttributeError) as e:
        LOGGER.debug("Failed to format %s front matter: %s", format_type, e)
        if strict:
            raise
        raise FormatError(content) from e
    except Exception as e:
        LOGGER.warning(
            "Unexpected error formatting %s front matter: %s", format_type, e
        )
        if strict:
            raise
        raise FormatError(content) from e


def _format_with_handler(
    content: str,
    handler: Any,  # Handler instance  # noqa: ANN401
    parse_func: Any,  # Parsing function (YAML().load, toml.loads, etc.)  # noqa: ANN401
    *,
    sort_keys: bool = True,
    normalize_mode: str = "none",
) -> str:
    """Format front matter using a handler and parsing function.

    Args:
        content: Raw front matter content (without delimiters).
        handler: Handler instance with export() method.
        parse_func: Function to parse content (YAML().load, toml.loads, etc.).
        sort_keys: Whether to sort keys in the front matter.
        normalize_mode: Normalization level passed through to the handler.

    Returns:
        Formatted front matter (without delimiters).

    Raises:
        TypeError: When metadata is not a dictionary.
        ValueError: When metadata contains no valid key-value pairs.
    """
    metadata = parse_func(content)

    if not isinstance(metadata, dict):
        msg = f"Front matter must be key-value pairs, got {type(metadata).__name__}"
        raise TypeError(msg)

    if not metadata:
        if not content.strip():
            return ""
        msg = "Front matter contains no valid key-value pairs"
        raise ValueError(msg)

    return handler.export(metadata, sort_keys=sort_keys, normalize_mode=normalize_mode).strip()


def format_yaml(content: str, *, strict: bool = False, sort_keys: bool = True, normalize_mode: str = "none") -> str:
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.
        normalize_mode: Normalization level — ``"none"`` preserves everything,
            ``"minimal"`` strips unnecessary quotes and normalizes null/booleans,
            ``"1.2"`` additionally upgrades YAML 1.1 boolean words (yes/no/on/off
            and variants) to ``true``/``false``.

    Returns:
        Formatted YAML string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "YAML", strict=strict):
            loader_yaml = YAML()
            if normalize_mode in ("none", "1.2"):
                loader_yaml.preserve_quotes = True
            return _format_with_handler(
                content,
                _RoundTripYAMLHandler(),
                loader_yaml.load,
                sort_keys=sort_keys,
                normalize_mode=normalize_mode,
            )
    except FormatError as err:
        return err.content


def format_toml(content: str, *, strict: bool = False, sort_keys: bool = True, normalize_mode: str = "none") -> str:
    """Format TOML front matter content.

    Args:
        content: Raw TOML string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.
        normalize_mode: Accepted for API consistency; TOML output is always normalized
            regardless of this value.

    Returns:
        Formatted TOML string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "TOML", strict=strict):
            formatted = _format_with_handler(
                content,
                _SortingTOMLHandler(),
                toml.loads,
                sort_keys=sort_keys,
                normalize_mode=normalize_mode,
            )
            return _normalize_toml_output(formatted)
    except FormatError as err:
        return err.content


def format_json(content: str, *, strict: bool = False, sort_keys: bool = True, normalize_mode: str = "none") -> str:
    """Format JSON front matter content.

    Args:
        content: Raw JSON string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.
        normalize_mode: Accepted for API consistency; JSON output is always normalized
            regardless of this value.

    Returns:
        Formatted JSON string (without delimiters), or original content if
        formatting fails in non-strict mode.
    """
    try:
        with _handle_format_errors(content, "JSON", strict=strict):
            return _format_with_handler(
                content,
                _SortingJSONHandler(),
                json.loads,
                sort_keys=sort_keys,
                normalize_mode=normalize_mode,
            )
    except FormatError as err:
        return err.content
