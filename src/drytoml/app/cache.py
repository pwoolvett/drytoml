import shutil
from pathlib import Path

from drytoml import logger
from drytoml.paths import CACHE


class Cache:
    """Manage drytoml's internal cache"""

    @classmethod
    def clear(cls, force: bool = False, name: str = ""):
        """Clear drytoml's cache

        Args:
            force: Clear without asking.
            name: If set, only clear a specific cache element.

        """

        if not force:
            truthy = {"t", "true", "y", "yes", "clear"}
            response = input("Clear cache? [y/N]")
            if response.lower() not in truthy:
                logger.error("Aborted")
                raise SystemExit(1)

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
            logger.info(f"Succesfully cleared {CACHE} {name}")
        else:
            logger.info(f"Nothing cleared from {CACHE} ")
            raise SystemExit(1)

        return cls.show()

    @staticmethod
    def show():
        """Show drytoml's cache contents"""
        data = {
            descendant: descendant.stat().st_size
            for descendant in CACHE.glob("**/*")
            if descendant.is_file()
        }
        if not data:
            return logger.info(f"Cache is empty: {CACHE}")
        info = {
            **{k: f"{v/1024:.2f} kb" for k, v in data.items()},
            "__total__": f"{sum(data.values()) / 1024:.2f} kb",
        }
        return info
