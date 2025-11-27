"""An mdformat plugin for `front_matters`."""

__version__ = "1.0.0"

__plugin_name__ = "front_matters"

# FYI see source code for available interfaces:
#   https://github.com/executablebooks/mdformat/blob/5d9b573ce33bae219087984dd148894c774f41d4/src/mdformat/plugins.py
from .plugin import POSTPROCESSORS, RENDERERS, add_cli_argument_group, update_mdit

__all__ = ("POSTPROCESSORS", "RENDERERS", "add_cli_argument_group", "update_mdit")
