# -*- coding: utf-8 -*-
"""Manage drytoml's internal cache.

This module contains the Cache class, which allows fire to execute any
method (bound, static, or classmethod) as sub-command from the cli.
"""

import shutil
import sys
from pathlib import Path
from typing import Dict
from typing import Union

from drytoml import logger
from drytoml.paths import CACHE


class Cache:
    """Manage drytoml's internal cache."""

    @classmethod
    def clear(
        cls, force: bool = False, name: str = ""
    ) -> Dict[Union[Path, str], str]:
        """Clear drytoml's cache.

        Args:
            force: Clear without asking.
            name: If set, only clear a specific cache element.

        Returns:
            Contents of the cache after clearing it.

        """

        if not force:
            truthy = {"t", "true", "y", "yes", "clear"}
            response = input("Clear cache? [y/N]")
            if response.lower() not in truthy:
                logger.error("Aborted")
                sys.exit(1)

        worked = False
        for descendant in CACHE.glob("**/*"):
            if name and (descendant.stem != Path(name).stem):
                continue

            if descendant.is_file():
                descendant.unlink()
                worked = True
            elif descendant.is_dir():
                shutil.rmtree(str(descendant.resolve()))
                worked = True
        if worked:
            logger.info("Succesfully cleared {} {}", CACHE, name)
        else:
            logger.info("Nothing cleared from {}", CACHE)
            sys.exit(1)

        return cls.show()

    @staticmethod
    def show() -> Dict[Union[str, Path], str]:
        """Show drytoml's cache contents.

        Returns:
            Locations -> weight (in kb) mapping
        """
        data = {
            descendant: descendant.stat().st_size
            for descendant in CACHE.glob("**/*")
            if descendant.is_file()
        }
        if not data:
            return logger.info("Cache is empty: {}", CACHE)
        info = {
            **{k: f"{v/1024:.2f} kb" for k, v in data.items()},
            "__total__": f"{sum(data.values()) / 1024:.2f} kb",
        }
        return info
