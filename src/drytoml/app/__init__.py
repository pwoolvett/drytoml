#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
import functools
import logging
from enum import IntEnum
import sys
import fire

from drytoml.app.cache import Cache

LOG_LEVEL = IntEnum("LOG_LEVEL", logging._nameToLevel)
from drytoml import logger
# CRITICAL = 50
# ERROR = 40
# WARNING = 30
# INFO = 20
# DEBUG = 10
# NOTSET = 0

ALL_COMMANDS = {
    cls.__name__.lower(): cls
    for cls in (Cache,)
}

def setup_log(argv):
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_mutually_exclusive_group()
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='count', default=0)
    args, unknown = parser.parse_known_args()
    level = max(1,20 + 50*args.quiet - 10*args.verbose )
    logging.basicConfig(level=level, format='%(message)s', force=True)
    for lvl in ("critical","error","warning","info","debug"):
        getattr(logger, lvl)(lvl)
    return sys.argv[:1]+unknown


def main():
    sys.argv = setup_log(sys.argv)
    fire.Fire(ALL_COMMANDS)

if __name__ == '__main__':
    main()
