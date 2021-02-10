import os
from pathlib import Path
import shutil
from drytoml.paths import CACHE

class Cache:

    @classmethod
    def clear(
        cls,
        force:bool = False,
        name:str = ""
    ):
        """Clear drytoml's cache

        Args:
            force: Clear without asking.
            name: If set, only clear a specific cache element.

        """

        if not force:
            truthy = {"t", "true", "y", "yes", "clear"}
            response = input("Clear cache? [y/N]")
            if response.lower() not in truthy:
                print("Aborted")
                return

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
            print(f"Succesfully cleared {CACHE} {name}")
        else:
            print(f"Nothing cleared from {CACHE} ")
            raise SystemExit(1)

        return cls.show()

    @staticmethod
    def show():
        data = {
            descendant: descendant.stat().st_size
            for descendant in CACHE.glob("**/*")
            if descendant.is_file()
        }
        if not data:
            return print(f"Cache is empty: {CACHE}")
        info = {
            **{
                k: f"{v/1024:.2f} kb"
                for k,v in data.items()
            },
            "__total__": f"{sum(data.values()) / 1024:.2f} kb"
        }
        return info
