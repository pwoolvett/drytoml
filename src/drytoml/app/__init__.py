#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cli application for drytoml."""
import argparse
import logging
import sys
from typing import List
from typing import Optional

import fire

from drytoml import logger
from drytoml.app.cache import Cache
from drytoml.app.explain import explain
from drytoml.app.export import export
from drytoml.app.wrappers import black
from drytoml.app.wrappers import flake8helled
from drytoml.app.wrappers import flakehell
from drytoml.app.wrappers import isort
from drytoml.app.wrappers import pylint

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
        pylint,
        flakehell,
        flake8helled,
    )
}


def setup_log(argv: Optional[List[str]]) -> List[str]:
    """Control verbosity via logging level using "-q/-v" as flags.

    Args:
        argv: If not set, use sys.argv. For each "-v" or "--verbose",
              increase the log level verbosity. If it contains a "-q",
              or a "--quiet", set lefel to `logging.CRITICAL`.

    Returns:
        Unparsed, remanining arguments.
    """

    argv = argv or sys.argv

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_mutually_exclusive_group()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="count", default=0)
    args, unknown = parser.parse_known_args()
    level = max(1, 20 + 50 * args.quiet - 10 * args.verbose)
    logging.basicConfig(level=level, format="%(message)s", force=True)
    logger.debug(
        "drytoml: Log level set to {} because {}", level, args.__dict__
    )
    return sys.argv[:1] + unknown


def main():
    """Execute the cli application.

    Returns:
        The result of the wrapped command
    """
    sys.argv = setup_log(sys.argv)

    if len(sys.argv) == 1 or sys.argv[1] not in WRAPPERS:
        return fire.Fire(INTERNAL_CMDS)

    del sys.argv[0]
    return WRAPPERS[sys.argv[0]]()


if __name__ == "__main__":
    main()
