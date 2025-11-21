# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-XX

### Added

- Initial production release of mdformat-front-matters plugin
- Support for YAML front matter (delimited by `---`)
- Support for TOML front matter (delimited by `+++`)
- Support for JSON front matter (delimited by `{...}`)
- Automatic normalization of front matter formatting
- `--strict-front-matter` CLI option for validation mode (fail on invalid front matter)
- Comprehensive error handling with logging (debug and warning levels)
- Preserves original content when parsing fails (prevents data loss)
- HTML rendering support (front matter excluded from HTML output)
- Improved JSON parsing with proper string context handling
- Extensive test coverage (80 tests total):
    - 26 format tests
    - 4 render tests
    - 14 helper tests
    - 17 security and edge case tests
    - 9 strict mode tests
    - 9 performance benchmarks
- Performance benchmarks ensure reasonable execution speed
- 90% code coverage

### Changed

- TOML sections may be reordered alphabetically (semantic equivalence maintained)
- Array spacing normalized in TOML output (e.g., `[ "item"` → `["item"]`)
- Unicode characters (e.g., emojis) rendered as actual characters in YAML instead of escape sequences
- Empty front matter (no valid key-value pairs) preserved instead of deleted

### Fixed

- Data loss bug: Front matter with no valid key-value pairs now preserved
- TOML formatting with nested tables and arrays of tables
- Trailing commas removed from TOML arrays
- Blank line normalization in TOML output
- Unicode character handling in YAML front matter
- JSON brace counting now respects string context (handles `{braces}` in strings)

### Security

- Safe handling of YAML anchors and tags (prevents code execution)
- Tested with large documents (1000+ entries) and deep nesting (100+ levels)
- All malformed content preserved safely without crashes

## [0.0.1] - Never released

Initial development version.

[0.0.1]: https://github.com/kyleking/mdformat-front-matters/releases/tag/v0.0.1
[0.1.0]: https://github.com/kyleking/mdformat-front-matters/releases/tag/v0.1.0
[unreleased]: https://github.com/kyleking/mdformat-front-matters/compare/v0.1.0...HEAD
