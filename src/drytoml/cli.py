# -*- coding: utf-8 -*-
""""""
import sys

from drytoml.reader import Toml


def black():
    from black import patched_main
    try:
        idx = sys.argv.index("--config")
        pre = sys.argv[:idx]
        post = sys.argv[idx+2:]
        cfg = sys.argv[idx+1]
    except ValueError:
        pre = sys.argv
        post = []
        cfg = "pyproject.toml"


    merged = Toml(cfg)

    with merged.virtual() as virtual:
        sys.argv = [*pre, "--config", f"{virtual.name}", *post]
        patched_main()

def isort():
    from isort.main import main
    for option in {
        "--sp",
        "--settings-path",
        "--settings-file",
        "--settings",
    }:
        try:
            idx = sys.argv.index(option)
            pre = sys.argv[:idx]
            post = sys.argv[idx+2:]
            cfg = sys.argv[idx+1]
            break
        except ValueError:
            pass
    else:
        pre = sys.argv
        post = []
        cfg = "pyproject.toml"


    merged = Toml(cfg)


    with merged.virtual() as virtual:
        print(str(virtual.name))
        sys.argv = [*pre, "--settings-path", f"{virtual.name}", *post]
        main()
