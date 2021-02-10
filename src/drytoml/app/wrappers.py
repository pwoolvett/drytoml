import importlib
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from drytoml.parser import Parser


@contextmanager
def tmp_dump(cfg: str):
    parser = Parser.from_file(cfg)
    document = parser.parse()

    # ensure locally referenced files work
    path = Path(cfg)
    if path.is_absolute():
        parent = path.parent
    else:
        parent = (Path.cwd() / cfg).parent

    with tempfile.NamedTemporaryFile(
        mode="w+",
        suffix=".toml",
        prefix="drytoml.",
        dir=str(parent),
    ) as fp:
        fp.write(document.as_string())
        fp.seek(0)
        yield fp


def import_callable(string):
    module_str, tool_main_str = string.split(":")
    module = importlib.import_module(module_str)
    tool_main = getattr(module, tool_main_str)
    return tool_main


def impl_cli(importstr, configs):
    tool_main = import_callable(importstr)
    for option in configs:
        try:
            idx = sys.argv.index(option)
            pre = sys.argv[:idx]
            post = sys.argv[idx + 2 :]
            cfg = sys.argv[idx + 1]
            break
        except ValueError:
            pass
    else:
        pre = sys.argv
        post = []
        cfg = "pyproject.toml"

    with tmp_dump(cfg) as virtual:
        sys.argv = [*pre, option, f"{virtual.name}", *post]

        sys.exit(tool_main())


def black():
    return impl_cli("black:patched_main", ["--config"])


def isort():
    return impl_cli(
        "isort.main:main",
        ["--sp", "--settings-path", "--settings-file", "--settings"],
    )
