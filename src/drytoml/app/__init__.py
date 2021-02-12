#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
import logging
import sys

import fire

from drytoml import logger
from drytoml.app.cache import Cache
from drytoml.app.explain import explain
from drytoml.app.export import export
from drytoml.app.wrappers import black
from drytoml.app.wrappers import flake8helled
from drytoml.app.wrappers import flakehell
from drytoml.app.wrappers import isort

INTERNAL_CMDS = {
    cmd.__name__.lower(): cmd
    for cmd in (
        Cache,
        explain,
        export,
    )
}

WRAPPERS = {
    cmd.__name__.lower(): cmd
    for cmd in (
        black,
        isort,
        flakehell,
        flake8helled,
    )
}


def setup_log(argv):
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_mutually_exclusive_group()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="count", default=0)
    args, unknown = parser.parse_known_args()
    level = max(1, 20 + 50 * args.quiet - 10 * args.verbose)
    logging.basicConfig(level=level, format="%(message)s", force=True)
    logger.debug(f"drytoml: Log level set to {level} because {args.__dict__}")
    return sys.argv[:1] + unknown


def main():
    sys.argv = setup_log(sys.argv)

    if len(sys.argv) == 1 or sys.argv[1] not in WRAPPERS:
        return fire.Fire(INTERNAL_CMDS)

    del sys.argv[0]
    return WRAPPERS[sys.argv[0]]()


if __name__ == "__main__":
    main()
