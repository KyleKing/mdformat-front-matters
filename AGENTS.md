# AI Contributor Guide

## Project Snapshot

- mdformat plugin that formats front matter blocks for CommonMark documents
- Plugin surface in `mdformat_front_matters/` (`__init__.py`, `plugin.py`, `_helpers.py`)
- Tests live in `tests/` with behavior suites in `format/` and `render/`, shared helpers in `tests/helpers.py`

## Key Interfaces & Architecture

- Entry points declared in `pyproject.toml` under `mdformat.parser_extension`
- `mdformat_front_matters.__all__` exports `update_mdit`, `RENDERERS`, `POSTPROCESSORS`, `add_cli_argument_group`
- Implement a markdown-it plugin (`front_matters_plugin`) and register it via `update_mdit`
- Renderer/postprocessor callables must use snake_case token-type names; keep supporting utilities beside the plugin so Flit packages them
- Retrieve plugin configuration with `_helpers.get_conf(context.options, "key")` to support CLI, API, and TOML sources

## Workflow Cheatsheet

- Tests & coverage: `tox -e py312-test`; targeted run `pytest tests/format/test_format.py -vv`
- Lint/format: `tox -e py312-ruff`; direct `ruff check . --fix` and `ruff format .`
- Typing: `tox -e py312-type` or `mypy mdformat_front_matters`
- Pre-commit stack: `tox -e py312-pre-commit`; run all envs with `tox -p auto`
- Rapid feedback: `ptw .` leverages pytest-watcher defaults

## Testing Expectations

- Use pytest with beartype; name modules and functions `test_*`
- Parser fixtures live in `tests/format/fixtures/`, renderer snapshots in `tests/render/fixtures/`
- Add regression examples before fixes and keep `pytest --cov=mdformat_front_matters` stable across changes

## Coding Standards

- Python ≥3.9, four-space indentation, Ruff-enforced 88-character lines
- Prefer Google-style docstrings with explicit typing
- Export public symbols via `__all__` in `__init__.py`; ensure renderer mappings stay in sync with markdown-it token names

## Release & Packaging

- Do not release automatically
