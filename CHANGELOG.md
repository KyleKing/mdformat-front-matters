# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of mdformat-front-matters plugin
- Support for YAML front matter (delimited by `---`)
- Support for TOML front matter (delimited by `+++`)
- Support for JSON front matter (delimited by `{...}`)
- Automatic normalization of front matter formatting
- Comprehensive error handling with logging
- Preserves original content when parsing fails
- HTML rendering support (front matter excluded from HTML output)
- Extensive test coverage including edge cases and security tests

### Changed
- TOML sections may be reordered alphabetically (semantic equivalence maintained)
- Array spacing normalized in TOML output
- Unicode characters (e.g., emojis) rendered as actual characters in YAML instead of escape sequences

### Fixed
- TOML formatting with nested tables and arrays of tables
- Trailing commas removed from TOML arrays
- Blank line normalization in TOML output
- Unicode character handling in YAML front matter

## [0.0.1] - Not yet released

Initial development version.

[Unreleased]: https://github.com/kyleking/mdformat-front-matters/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/kyleking/mdformat-front-matters/releases/tag/v0.0.1
