# -*- coding: utf-8 -*-
""""""
import importlib
import sys
import tempfile
from contextlib import contextmanager

from drytoml.parser import Parser

PROVIDERS = {
    "black": ("black:patched_main", ["--config"]),
    "isort": (
        "isort.main:main",
        ["--sp", "--settings-path", "--settings-file", "--settings"],
    ),
}


@contextmanager
def tmp_dump(cfg: str):
    parser = Parser.from_file(cfg)
    document = parser.parse()
    with tempfile.NamedTemporaryFile(
        mode="w+",
        suffix=".toml",
        prefix="drytoml.black",
    ) as fp:
        fp.write(document.as_string())
        fp.seek(0)
        yield fp


def import_callable(string):
    module_str, tool_main_str = string.split(":")
    module = importlib.import_module(module_str)
    tool_main = getattr(module, tool_main_str)
    return tool_main


def impl(importstr, configs):
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
    from black import patched_main

    try:
        idx = sys.argv.index("--config")
        pre = sys.argv[:idx]
        post = sys.argv[idx + 2 :]
        cfg = sys.argv[idx + 1]
    except ValueError:
        pre = sys.argv
        post = []
        cfg = "pyproject.toml"

    with tmp_dump(cfg) as virtual:
        sys.argv = [*pre, "--config", f"{virtual.name}", *post]
        patched_main()

def main():
    del sys.argv[0]
    provider = sys.argv[0]
    return impl(*PROVIDERS[provider])


if __name__ == "__main__":
    black()
