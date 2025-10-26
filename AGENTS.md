# AI Contributor Guide

## Project Overview

- mdformat plugin that normalizes YAML/TOML front matter blocks for CommonMark documents.
- Primary code lives in `mdformat_front_matters/` (`__init__.py`, `plugin.py`, `_helpers.py`); tests reside under `tests/` with behavior fixtures in `format/` and `render/`.

## Setup Commands

- Create a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install the project with extras: `pip install -e ".[test]"`
- Reuse `tox -p auto` for all defined environments when you need a clean sweep.

## Build & Test Commands

- Run full test + coverage: `tox -e py312-test`
- Target a suite: `pytest tests/format/test_format.py -vv --cov=mdformat_front_matters`
- Lint + format: `tox -e py312-ruff` (or `ruff check . --fix` / `ruff format .`)
- Type checking: `tox -e py312-type` or `mypy mdformat_front_matters`
- Pre-commit hooks: `tox -e py312-pre-commit`
- Rapid loop: `ptw .` leverages the pytest-watcher defaults from `tool.pytest-watcher`

## Key Interfaces & Architecture

- Entry point declared in `pyproject.toml` under `mdformat.parser_extension`.
- `mdformat_front_matters.__all__` exports `update_mdit`, `RENDERERS`, `POSTPROCESSORS`, and `add_cli_argument_group`.
- The markdown-it plugin (`front_matters_plugin`) is registered via `update_mdit`; renderer/postprocessor callables must use snake_case token names.
- Retrieve plugin configuration via `_helpers.get_conf(context.options, "key")` so CLI, API, and pyproject sources stay consistent.

## Code Style Guidelines

- Python ≥3.9, four-space indentation, Ruff-enforced 88-character lines.
- Prefer Google-style docstrings with explicit typing; keep public exports declared in `__all__`.
- Align renderer mappings with the markdown-it token names and keep helper utilities co-located so Flit packages them.

## Testing Instructions

- Use pytest with beartype; name new modules/functions `test_*`.
- Parser fixtures live in `tests/format/fixtures/`, renderer snapshots in `tests/render/fixtures/`, shared helpers in `tests/helpers.py`.
- Add regression fixtures before fixes and keep `pytest --cov=mdformat_front_matters` coverage stable.

## Security Considerations

- Never embed real secrets or production front matter in fixtures; sanitize sample metadata.
- The formatter should stay purely deterministic—avoid introducing network access, file writes outside the workspace, or dynamic code execution.
- Validate front matter parsing defensively and prefer schema checks or graceful fallbacks over raising uncaught exceptions.

## Additional Instructions

- Run lint, type, and test tox environments before submitting patches; refresh README examples when CLI or formatter behavior changes.
- Document noteworthy behavior changes in the README (or upcoming release notes) and keep CLI argument docs in sync.
- For pull requests, include a brief summary of coverage impact and mention any new configuration keys added via `_helpers.get_conf`.

## Release & Packaging

- Distributions are managed with Flit; do not publish from agent sessions.
