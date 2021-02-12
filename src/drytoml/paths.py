"""Common filesystem paths for drytoml."""

import os
from pathlib import Path
from typing import Union


def env_or(xdg_env: str, home_subdir: Union[str, Path]) -> Path:
    """Retreive path from xdg env, with home subdir as default.

    Args:
        xdg_env: Name of the environment variable.
        home_subdir: Sub-directory (inside $HOME) to use as default
            value if the env var is not found.

    Returns:
        Resulting path

    Examples:

        For an exising env var:
        >>> env_or("XDG_CACHE_HOME", ".cache/custom")
        PosixPath('/home/vscode/.cache')

        For an env var not present:
        >>> env_or("XDG_DATA_HOME", ".custom_subdir")
        PosixPath('/home/vscode/.custom_subdir')
    """
    return Path(os.environ.get(xdg_env, Path.home() / home_subdir))


CACHE = env_or("XDG_CACHE_HOME", ".cache") / "drytoml"
"""Location of drytoml's cache.
It can be overriden by changing the XDG_CACHE_HOME env var.
"""

CONFIG = env_or("XDG_CONFIG_HOME", ".config") / "drytoml"
"""Location of drytoml's configuration files.
It can be overriden by changing the XDG_CONFIG_HOME env var.
"""
