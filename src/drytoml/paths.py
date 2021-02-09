import os
from pathlib import Path


def env_or(xdg_env, home_subdir):
    return Path(os.environ.get(xdg_env, Path.home() / home_subdir))


CACHE = env_or("XDG_CACHE_HOME", ".cache") / "drytoml"

CONFIG = env_or("XDG_CONFIG_HOME", ".config") / "drytoml"
