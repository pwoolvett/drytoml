import os
from pathlib import Path

CACHE = Path(
    os.environ.get("XDG_CACHE_HOME", Path.home()/".cache")
) / "drytoml"

CONFIG = Path(
    os.environ.get("XDG_CONFIG_HOME", Path.home()/".config")
) / "drytoml"
