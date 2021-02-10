#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
import fire
from drytoml.app.cache import Cache

ALL_COMMANDS = {
    cls.__name__.lower():cls
    for cls in (Cache,)
}

def main():
    fire.Fire(ALL_COMMANDS)

if __name__ == '__main__':
    main()
