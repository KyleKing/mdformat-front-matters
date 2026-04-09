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
from ruamel.yaml.nodes import ScalarNode
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


def _as_yaml12_bool(value: str) -> bool | None:
    if value in _YAML11_TRUE_WORDS:
        return True
    if value in _YAML11_FALSE_WORDS:
        return False
    return None


def _represent_as_plain_str(dumper: _RoundTripRepresenter, data: object) -> ScalarNode:
    return dumper.represent_str(str.__new__(str, data))


class _NullNormalizingRepresenter(_RoundTripRepresenter):
    """Representer for normalize modes.

    Overrides at the representer level rather than walking the tree post-load,
    because ``_RoundTripRepresenter`` registers a ``ScalarString`` representer
    that is found via MRO before the base ``str`` representer — a tree walk
    converting to plain ``str`` would still hit that path.

    ``SingleQuotedScalarString`` / ``DoubleQuotedScalarString`` → plain scalars
    (strips quote style the loader preserved for YAML 1.1 boolean detection).
    ``LiteralScalarString`` / ``FoldedScalarString`` deliberately excluded so
    block scalar styles (``|``, ``>``) are always preserved.
    ``None`` → ``null`` (not ``~``).
    """


_NullNormalizingRepresenter.add_representer(
    type(None),
    lambda d, _: d.represent_scalar("tag:yaml.org,2002:null", "null"),
)
_NullNormalizingRepresenter.add_representer(SingleQuotedScalarString, _represent_as_plain_str)
_NullNormalizingRepresenter.add_representer(DoubleQuotedScalarString, _represent_as_plain_str)


class _RoundTripYAMLHandler:
    """YAML round-trip handler preserving unicode, comments, and configurable quote style.

    ruamel.yaml wraps quoted scalars in ``SingleQuotedScalarString`` /
    ``DoubleQuotedScalarString`` when ``preserve_quotes=True``, and block scalars
    in ``LiteralScalarString`` / ``FoldedScalarString`` unconditionally.
    See: https://sourceforge.net/p/ruamel-yaml/code/ci/default/tree/constructor.py#l985
    """

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        sort_keys = kwargs.pop("sort_keys", True)
        normalize_mode = str(kwargs.pop("normalize_mode", "none"))

        yaml = YAML()
        if normalize_mode == "none":
            yaml.preserve_quotes = True
        else:
            yaml.Representer = _NullNormalizingRepresenter
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        yaml.width = (
            kwargs.pop("wrap", None) or sys.maxsize
        )  # Prevent line wrapping by default

        # Consistent indentation for previous mdformat-frontmatter users:
        # https://github.com/butler54/mdformat-frontmatter/blob/93bb972b6044d22043d6c191a2e73858ff09d3e5/mdformat_frontmatter/plugin.py#L14
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
        """Sort keys in-place using ``CommentedMap.insert()`` to preserve EOL comments.

        ``pop()`` detaches comments from keys; ``insert()`` re-associates them.
        Based on: https://stackoverflow.com/a/51387713/3219667
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
        """Convert unquoted YAML 1.1 boolean words to Python booleans.

        Quoted values (``SingleQuotedScalarString`` / ``DoubleQuotedScalarString``)
        are skipped — the author explicitly quoted them to signal "this is a string,
        not a boolean". The loader must have used ``preserve_quotes=True`` for this
        distinction to be available; ``minimal`` mode omits that and thus cannot
        safely upgrade YAML 1.1 booleans.
        """
        if isinstance(data, dict):
            for key in data:
                value = data[key]
                if isinstance(value, str) and not isinstance(
                    value, (SingleQuotedScalarString, DoubleQuotedScalarString)
                ):
                    if (converted := _as_yaml12_bool(value)) is not None:
                        data[key] = converted
                elif isinstance(value, (dict, list)):
                    self._upgrade_yaml11_booleans(value)
        elif isinstance(data, list):
            self._upgrade_yaml11_booleans_in_list(data)

    def _upgrade_yaml11_booleans_in_list(
        self, data: CommentedSeq | list[object]
    ) -> None:
        for i, item in enumerate(data):
            if isinstance(item, str) and not isinstance(
                item, (SingleQuotedScalarString, DoubleQuotedScalarString)
            ):
                if (converted := _as_yaml12_bool(item)) is not None:
                    data[i] = converted
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
        super().__init__()
        self.content = content


@contextmanager
def _handle_format_errors(
    content: str,
    format_type: str,
    *,
    strict: bool,
) -> Generator[None, None, None]:
    """Context manager: non-strict wraps errors in ``FormatError``; strict re-raises."""
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
    handler: Any,  # noqa: ANN401
    parse_func: Any,  # noqa: ANN401
    *,
    sort_keys: bool = True,
    normalize_mode: str = "none",
    wrap: int | None = None,
) -> str:
    """Parse ``content`` and export via ``handler``."""
    metadata = parse_func(content)

    if not isinstance(metadata, dict):
        msg = f"Front matter must be key-value pairs, got {type(metadata).__name__}"
        raise TypeError(msg)

    if not metadata:
        if not content.strip():
            return ""
        msg = "Front matter contains no valid key-value pairs"
        raise ValueError(msg)

    return handler.export(metadata, sort_keys=sort_keys, normalize_mode=normalize_mode, wrap=wrap).strip()


def format_yaml(
    content: str,
    *,
    strict: bool = False,
    sort_keys: bool = True,
    normalize_mode: str = "none",
    wrap: int | None = None,
    """Format YAML front matter content.

    Args:
        content: Raw YAML string to format (without delimiters).
        strict: If True, raise exceptions instead of preserving original.
        sort_keys: If True, sort keys alphabetically.
        normalize_mode: ``"none"`` round-trips everything unchanged; ``"minimal"``
            strips unnecessary quotes, normalizes null and boolean casing;
            ``"1.2"`` additionally converts unquoted YAML 1.1 boolean words
            (``yes``/``no``/``on``/``off`` and variants) to ``true``/``false``.
        wrap: Line length limit, if any.

    Returns:
        Formatted YAML (without delimiters), or original on failure in non-strict mode.

    Note:
        ``"none"`` and ``"1.2"`` both load with ``preserve_quotes=True`` so the
        loader wraps quoted scalars in ``DoubleQuotedScalarString`` /
        ``SingleQuotedScalarString``. For ``"1.2"`` this lets the boolean upgrader
        distinguish intentionally quoted ``"yes"`` (keep as string) from unquoted
        ``yes`` (YAML 1.1 boolean → ``true``). For ``"none"`` the dumper also sets
        ``preserve_quotes=True`` to honour that style on output. For ``"minimal"``
        neither is set — all strings load as plain ``str`` and the dumper applies
        minimal quoting.
    """
    try:
        with _handle_format_errors(content, "YAML", strict=strict):
            loader_yaml = YAML()
            if normalize_mode in {"none", "1.2"}:
                loader_yaml.preserve_quotes = True
            return _format_with_handler(
                content,
                _RoundTripYAMLHandler(),
                loader_yaml.load,
                sort_keys=sort_keys,
                normalize_mode=normalize_mode,
                wrap=wrap,
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
