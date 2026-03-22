# mdformat-front-matters

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

An [mdformat](https://github.com/executablebooks/mdformat) plugin for normalizing YAML, TOML, and JSON front matter in CommonMark documents.

> [!NOTE]
> [`mdformat-frontmatter`](https://github.com/butler54/mdformat-frontmatter) has additional duplicate key detection, but did not support mdformat v1 ([butler54/mdformat-frontmatter #37](https://github.com/butler54/mdformat-frontmatter/issues/37)) nor TOML and JSON at the time ([https://github.com/butler54/mdformat-frontmatter/issues/22#issuecomment-1815433725](https://github.com/butler54/mdformat-frontmatter/issues/22#issuecomment-1815433725))
>
> Along with the 's', the extra dash is intentional to try to prevent typo errors.

## Features

- **Multi-format support**: Handles YAML (`---`), TOML (`+++`), and JSON (`{...}`) front matter
- **Automatic normalization**: Formats front matter consistently (preserves key order by default, standardized indentation)
- **Quote preservation**: YAML string quotes (`"double"`, `'single'`, `|` block literal, `>` block folded) are preserved by default
- **Configurable sorting**: Option to sort keys alphabetically with `--sort-front-matter`
- **Quote normalization**: Option to strip unnecessary YAML quotes with `--normalize-front-matter`
- **Error resilient**: Preserves original content if parsing fails. Will error only if `strict` mode is set
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

With `--sort-front-matter`, becomes:

```markdown
---
date: 2024-01-01
tags:
  - example
  - demo
title: My Document
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

### pre-commit / prek

```yaml
repos:
  - repo: https://github.com/executablebooks/mdformat
    rev: 1.0.0
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-front-matters
```

### uvx

```sh
uvx --with mdformat-front-matters mdformat
```

Or with pipx:

```sh
pipx install mdformat
pipx inject mdformat mdformat-front-matters
```

### Configuration Options

All options are independent and composable — use any combination.

#### Key Sorting

By default, front matter keys preserve their original order. To sort keys alphabetically for consistency, use the `--sort-front-matter` flag.

```sh
# Default behavior - preserves original key order
mdformat document.md

# Sort keys alphabetically
mdformat document.md --sort-front-matter
```

#### YAML Quote Normalization

By default, YAML string quote styles are preserved exactly as written — double-quoted, single-quoted, and block scalars (`|`, `>`) all round-trip unchanged. Use `--normalize-front-matter` to strip unnecessary quotes from plain string values.

```sh
# Default behavior - preserves quote style
mdformat document.md

# Strip unnecessary quotes
mdformat document.md --normalize-front-matter
```

Before:

```yaml
---
title: "My Post"
author: 'Jane Doe'
description: |
  A multi-line
  description.
---
```

After `--normalize-front-matter`:

```yaml
---
title: My Post
author: Jane Doe
description: |
  A multi-line
  description.
---
```

Quotes that are semantically necessary are always preserved — for example, values containing colons (`value: with colon`), bool-like strings (`"true"`, `"false"`), and empty strings (`""`). Block scalar styles (`|` and `>`) are always preserved regardless of this option.

TOML and JSON are unaffected by `--normalize-front-matter` since they are always output in a canonical form.

#### Strict Mode

Enable strict mode to fail on invalid front matter instead of preserving it. Useful for CI/CD pipelines.

```sh
mdformat document.md --strict-front-matter
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

#### Configuration File

All options can be set in `.mdformat.toml` instead of passing CLI flags:

```toml
[plugin.front_matters]
sort_front_matter = true
normalize_front_matter = true
strict_front_matter = true
```

Or via the Python API:

```python
import mdformat

mdformat.text(
    content,
    extensions={"front_matters"},
    options={"plugin": {"front_matters": {"normalize_front_matter": True}}},
)
```

## HTML Rendering

To hide Front Matter from generated HTML output, `front_matters_plugin` can be imported from `mdit_plugins`. For more guidance on `MarkdownIt`, see the docs: <https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser>

```py
from markdown_it import MarkdownIt

from mdformat_front_matters.mdit_plugins import front_matters_plugin

md = MarkdownIt()
md.use(front_matters_plugin)

text = """
+++
title = "Example"
draft = false
+++
# Example
"""
md.render(text)
# <h1>Example</h1>
```

## Contributing

See [CONTRIBUTING.md](https://github.com/kyleking/mdformat-front-matters/blob/main/CONTRIBUTING.md)

[ci-badge]: https://github.com/kyleking/mdformat-front-matters/actions/workflows/tests.yml/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-front-matters/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-front-matters.svg
[pypi-link]: https://pypi.org/project/mdformat-front-matters
