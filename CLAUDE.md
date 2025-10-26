# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an mdformat plugin for formatting front matter in Markdown files. mdformat is a CommonMark-compliant formatter, and this plugin extends it to handle front matter blocks (YAML metadata at the start of Markdown files).

The plugin integrates with mdformat's extension system through entry points defined in `pyproject.toml` (`project.entry-points."mdformat.parser_extension"`).

## Development Commands

Run tests with coverage:

```bash
tox -e py312-test
# Or for specific Python version
tox -e py39-test
```

Run a single test file:

```bash
pytest tests/format/test_format.py -vv
# With beartype runtime checking
pytest tests/format/test_format.py -vv --beartype-packages=mdformat_front_matters
```

Lint and format code:

```bash
tox -e py312-ruff
# Or directly
ruff check . --fix
ruff format .
```

Type check:

```bash
tox -e py312-type
# Or directly
mypy mdformat_front_matters
```

Run pre-commit checks:

```bash
tox -e py312-pre-commit
```

Test the pre-commit hook integration:

```bash
tox -e py39-hook
```

Run all environments in parallel:

```bash
tox -p auto
```

Watch mode for rapid iteration:

```bash
ptw .  # Uses pytest-watcher config from pyproject.toml
```

## Architecture

### Plugin Entry Points

The plugin exports four key interfaces from `mdformat_front_matters/__init__.py`:

- `update_mdit`: Registers the markdown-it parser plugin
- `RENDERERS`: Maps syntax tree node types to render functions
- `POSTPROCESSORS`: Maps node types to postprocessing functions (optional)
- `add_cli_argument_group`: Adds plugin-specific CLI arguments (optional)

### Current State & Template Structure

**IMPORTANT**: This is a template repository that is not yet fully implemented. Key missing pieces:

- The `mdit_plugins` module referenced in `plugin.py:12` does not exist yet
- The `front_matters_plugin` needs to be created to define the markdown-it parser extension
- The `RENDERERS` mapping in `plugin.py:42-44` uses a placeholder token type
- `demo.py` shows a working example using `mdit_py_plugins.front_matter` that can serve as reference

When implementing the actual plugin:

1. Create `mdformat_front_matters/mdit_plugins/` directory
1. Implement `front_matters_plugin` as a markdown-it parser extension
1. Update `RENDERERS` to map the correct token type from the parser
1. The plugin should follow the pattern in `demo.py` for YAML front matter handling

### Configuration System

Plugin options can be provided three ways (checked in `_helpers.py:get_conf`):

1. API: `mdformat.text(content, options={"mdformat": {"key": value}})`
1. CLI: Arguments added via `add_cli_argument_group` in `plugin.py:15-26`
1. TOML: Stored in `tool.mdformat.plugin.front_matters` section

Access plugin config via `get_conf(context.options, "key")` in render functions.

### Testing Structure

Tests are organized by concern:

- `tests/format/`: Tests for mdformat integration (formatting round-trips)
- `tests/render/`: Tests for markdown-it rendering (HTML output)
- `tests/helpers.py`: Shared test utilities
- Fixture files in `tests/*/fixtures/*.md`: Test cases with input/expected output

## Code Standards

- Python ≥3.9, four-space indentation, 88-character line limit
- Google-style docstrings with explicit typing
- Export public symbols via `__all__` in `__init__.py`
- Use snake_case names matching markdown-it token types for renderer functions
- Ruff enforces style; mypy and pyright provide type checking
- Register new renderers in `RENDERERS` dict, postprocessors in `POSTPROCESSORS`

## Version & Release

Version lives in `mdformat_front_matters/__init__.py` as `__version__`. Flit handles builds and publishing to PyPI. Tag releases as `vX.Y.Z` matching the `__version__` string.
