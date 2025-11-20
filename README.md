# mdformat-front-matters

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

An [mdformat](https://github.com/executablebooks/mdformat) plugin for normalizing YAML, TOML, and JSON front matter in CommonMark documents

## Features

- **Multi-format support**: Handles YAML (`---`), TOML (`+++`), and JSON (`{...}`) front matter
- **Automatic normalization**: Formats front matter consistently (sorted keys, standardized indentation)
- **Error resilient**: Preserves original content if parsing fails
- **Zero configuration**: Works out of the box with mdformat

## Examples

**YAML Front Matter:**
```markdown
---
title: My Document
date: 2024-01-01
tags:
  - example
  - demo
---

# Content
```

**TOML Front Matter:**
```markdown
+++
title = "My Document"
date = 2024-01-01
tags = ["example", "demo"]
+++

# Content
```

**JSON Front Matter:**
```markdown
{
    "title": "My Document",
    "date": "2024-01-01",
    "tags": ["example", "demo"]
}

# Content
```

## `mdformat` Usage

Add this package wherever you use `mdformat` and the plugin will be auto-recognized. No additional configuration necessary. See [additional information on `mdformat` plugins here](https://mdformat.readthedocs.io/en/stable/users/plugins.html)

### Pre-Commit

```yaml
repos:
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.19
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-front-matters
```

### pipx/uv

```sh
pipx install mdformat
pipx inject mdformat mdformat-front-matters
```

Or with uv:

```sh
uv tool run --from mdformat-front-matters mdformat
```

### Configuration Options

#### Strict Mode

Enable strict mode to fail on invalid front matter instead of preserving it. Useful for CI/CD pipelines.

```sh
mdformat --strict-front-matter document.md
```

In strict mode:
- Invalid front matter raises an error
- Front matter without valid key-value pairs raises an error
- Ensures your documents have correctly formatted metadata

Example usage in pre-commit:

```yaml
repos:
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.19
    hooks:
      - id: mdformat
        args: [--strict-front-matter]
        additional_dependencies:
          - mdformat-front-matters
```

## HTML Rendering

To generate HTML output, `front_matters_plugin` can be imported from `mdit_plugins`. For more guidance on `MarkdownIt`, see the docs: <https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser>

```py
from markdown_it import MarkdownIt

from mdformat_front_matters.mdit_plugins import front_matters_plugin

md = MarkdownIt()
md.use(front_matters_plugin)

text = "... markdown example ..."
md.render(text)
# <div>
#
# </div>
```

## Contributing

See [CONTRIBUTING.md](https://github.com/kyleking/mdformat-front-matters/blob/main/CONTRIBUTING.md) and [Repository Guidelines](./AGENTS.md).

[ci-badge]: https://github.com/kyleking/mdformat-front-matters/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-front-matters/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-front-matters.svg
[pypi-link]: https://pypi.org/project/mdformat-front-matters
