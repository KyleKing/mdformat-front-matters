# AGENTS.md

## Testing

```bash
# Run all tests using tox
tox

# Run tests with coverage (Python 3.14 - current version)
tox -e test

# Run tests with coverage (Python 3.10 - minimum version)
tox -e test-min

# Run specific tests with pytest flags
tox -e test -- --exitfirst --failed-first --new-first -vv --snapshot-update
```

## Linting and Formatting

```bash
# Run all pre-commit hooks (using prek)
tox -e prek
# Or run directly with prek
prek run --all

# Run ruff for linting and formatting
tox -e ruff
# With unsafe fixes
tox -e ruff -- --unsafe-fixes
```

## Type Checking

```bash
# Run mypy type checking
tox -e type
```

## Pre-commit Hook Testing

```bash
# Test the plugin as a pre-commit hook
tox -e hook-min
```

## One-Off Testing

```bash
# Create a development environment with local code installed
tox devenv .venv

# Test mdformat on inline content
echo '- \[test\]: value' | .venv/bin/mdformat - --extension front_matters 2>&1

# Test mdformat on a specific file
.venv/bin/mdformat tests/pre-commit-test.md --extension front_matters

# Run Python code with local package installed
.venv/bin/python3 << 'PYTHON'
import mdformat
output = mdformat.text("- \[test\]: value", extensions={"front_matters"})
print(output)
PYTHON
```

## Architecture

### Plugin System

The package implements mdformat's plugin interface with up to four key exports in `__init__.py`:

- `update_mdit`: Registers markdown-it parser extensions
- `add_cli_argument_group`: Optionally adds CLI flags
- `RENDERERS`: Maps syntax tree node types to render functions
- `POSTPROCESSORS`: Post-processes rendered output (list normalization, inline wrapping, deflist escaping)

### Core Components

**mdformat_front_matters/plugin.py**

- Entry point that configures the mdformat plugin, registers all mdit_plugins, defines custom renders, and handles CLI configuration options

### Configuration Options

All options are independent and composable. Configuration can be passed via:

1. CLI arguments: `--sort-front-matter`, `--normalize-front-matter`, `--strict-front-matter`
1. TOML config file (`.mdformat.toml`):
    ```toml
    [plugin.front_matters]
    sort_front_matter = true
    normalize_front_matter = "minimal"  # or "1.2" or "none"
    strict_front_matter = true
    ```
1. API: `mdformat.text(content, extensions={"front_matters"}, options={"plugin": {"front_matters": {...}}})`

Option semantics:

- `sort_front_matter`: Sort keys alphabetically (default: preserve original order)
- `normalize_front_matter`: YAML only — `"none"` (default) preserves everything; `"minimal"` strips unnecessary quotes, normalizes null (`~` → `null`) and boolean case; `"1.2"` additionally upgrades unquoted YAML 1.1 boolean words (`yes`/`no`/`on`/`off`) to `true`/`false`
- `strict_front_matter`: Raise on invalid front matter instead of preserving it (default: preserve original content on error)

### Testing Strategy

**Snapshot Testing**

- Test fixtures in `tests/format/fixtures/` and `tests/render/fixtures/`
- Main test file: `tests/test_mdformat.py` verifies idempotent formatting against `tests/pre-commit-test.md`

**Test Organization**

- `tests/format/`: Tests formatting output (input markdown → formatted markdown)
- `tests/render/`: Tests HTML rendering (markdown → HTML via markdown-it)

## Development Notes

- **Do not use `uv` commands**—there is no `uv.lock` file. Always use `tox` (installed via mise and available on PATH) which manages environments and dependencies.
