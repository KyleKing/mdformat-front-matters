# mdformat-front-matters

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

An [mdformat](https://github.com/executablebooks/mdformat) plugin for `<placeholder>`

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

See [CONTRIBUTING.md](https://github.com/kyleking/mdformat-front-matters/blob/main/CONTRIBUTING.md)

[ci-badge]: https://github.com/kyleking/mdformat-front-matters/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-front-matters/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-front-matters.svg
[pypi-link]: https://pypi.org/project/mdformat-front-matters
