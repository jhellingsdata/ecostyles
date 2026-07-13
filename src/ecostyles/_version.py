"""Version information.

The version is defined once in ``pyproject.toml`` (``[project] version``) and read
back here at runtime via the installed package metadata, so there is a single source
of truth. When running from an uninstalled source tree, fall back to ``0.0.0.dev0``.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ecostyles")
except PackageNotFoundError:  # not installed (e.g. running from a raw source checkout)
    __version__ = "0.0.0.dev0"
