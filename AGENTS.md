# Repository Guidelines

## Project Structure & Module Organization

`mdformat_front_matters/` houses the plugin surface (`__init__.py`, `plugin.py`, helpers in `_helpers.py`); keep new Markdown-It utilities beside them so they ship with the package (`py.typed` exposes typing). Tests live in `tests/` with behavior-focused suites under `format/` and `render/`, plus shared utilities in `tests/helpers.py`. Root configs (`pyproject.toml`, `CONTRIBUTING.md`) govern tooling.

## Build, Test, and Development Commands

Prefer tox: `tox -e py312-test` runs pytest with coverage, `tox -e py312-ruff` applies linting and formatting, `tox -e py312-pre-commit` mimics the CI hook stack, and `tox -e py312-type` invokes mypy. During focused work, use `pytest tests/format/test_format.py -vv` or `mypy mdformat_front_matters` for quicker feedback.

## Coding Style & Naming Conventions

Code targets Python ≥3.9 with four-space indentation. Ruff enforces style (88-character max); run `ruff check .` and `ruff format .` before committing. Use Google-style docstrings, explicit typing, and export public symbols via `__all__`. Register new renderer/postprocessor callables in `RENDERERS` or `POSTPROCESSORS` using snake_case names matching Markdown-It token types.

## Testing Guidelines

Pytest with beartype drives the suite; name modules and functions `test_*`. Put parser scenarios in `tests/format/fixtures/` and renderer snapshots in `tests/render/fixtures/`. Add a regression example before fixes and keep `pytest --cov=mdformat_front_matters` steady. Run `tox -p auto` before pushes to exercise the matrix concurrently.

## Commit & Pull Request Guidelines

History uses Conventional Commit prefixes (e.g., `feat: initialize based on template`), so keep subjects imperative and under 72 characters. PRs should recap the change, note verification commands, and link issues. Include Markdown samples or screenshots when altering output, and mention version bumps when `mdformat_front_matters/__init__.py` changes.

## Release & Packaging Notes

Flit handles distribution. Bump `__version__`, ensure tox environments pass (`tox -e py312-pre-commit py312-test py312-type`), update release notes, then tag `vX.Y.Z`. CI publishes when `PYPI_KEY` is configured; otherwise run `flit publish` locally with the same credentials.
