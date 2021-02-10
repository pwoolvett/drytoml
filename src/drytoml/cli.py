# -*- coding: utf-8 -*-
""""""
import importlib
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from drytoml import logger
from drytoml.parser import Parser

CLI_PROVIDERS = {
    "black": ("black:patched_main", ["--config"]),
    "isort": (
        "isort.main:main",
        ["--sp", "--settings-path", "--settings-file", "--settings"],
    ),
}

ENVIRON_PROVIDERS = {
    "flake8helled": ("flakehell:flake8_entrypoint", "FLAKEHELL_TOML"),
    "flakehell": ("flakehell:entrypoint", "FLAKEHELL_TOML"),
}


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


def impl_env(importstr, env):

    cfg = os.environ.get(env, "pyproject.toml")

    with tmp_dump(cfg) as virtual:
        os.environ[env] = virtual.name
        # NOTE: import should go after env definition just to be safe
        tool_main = import_callable(importstr)
        sys.exit(tool_main())


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


def main():
    del sys.argv[0]
    provider = sys.argv[0]

    if provider in CLI_PROVIDERS:
        args = CLI_PROVIDERS[provider]
        return impl_cli(*args)

    if provider in ENVIRON_PROVIDERS:
        args = ENVIRON_PROVIDERS[provider]
        return impl_env(*args)

    if provider in INTERNAL:
        return INTERNAL[provider]()

    logger.error(f"Invalid command {provider}")
    sys.exit(1)


if __name__ == "__main__":
    main()
