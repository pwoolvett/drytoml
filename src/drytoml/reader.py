from functools import partial
import json
from pathlib import Path
import re
from typing import Any
from typing import Callable
from typing import MutableMapping
from typing import Optional
from typing import Dict
from typing import Union


import toml

# from drytoml.config import get
from drytoml.merge import full_merge, merge
# from drytoml.merge import merge
from drytoml.utils import Cached
from drytoml.utils import is_url
from drytoml.utils import Url

# from drytoml.utils import Url
# from drytoml.utils import walk
# from drytoml.utils import enter

class Toml(metaclass=Cached):
    """toml with inheritance capcabilities"""

    def __init__(
        self,
        source: Union[str, Url, Path],
        base_key="extends",
    ):
        """

        Args:
            source: toml source file.
            base_key: Each time this is found in a value, it will use it
                as information to inherit data from external sources.
        """
        self.source = source
        self.base_key = base_key
        self._data: str = ""

    @property
    def raw_data(self) -> str:
        """Read the string from the source"""
        if self._data:
            return self._data

        if Path(self.source).exists():
            with open(self.source) as fp:
                self._data = fp.read()
        elif is_url(self.source):
            self._data = get(self.source)
        else:
            # TODO: add git+ssh support
            raise ValueError(f"source {self.source} is neither a valid file nor URL")
        return self._data

    @classmethod
    def load_raw(cls, string: str) -> MutableMapping[str, Any]:
        """Native dictionary as parsed by the toml library."""
        return toml.loads(string)

    def build_child(
        self,
        source: Union[str, Url, Path],
        base_key=None,
    ):
        cls = type(self)
        base_key = base_key or self.base_key
        path = Path(source)
        if (is_url(source) or is_url(str(self.source))) or (path.is_absolute()):
            return cls(source, base_key)

        # Ensure relative path with respect to this file
        path = (Path(self.source).parent / source).resolve()
        return cls(path, base_key)

    def merge_from_str(self, config, source, key=None):
        reference_data = self.build_child(source).load()
        if key:
            merge(reference_data, config, key)
        else:
            full_merge(reference_data, config)

    def merge_from_dict(self, config, source_instructions):
        for key, value in source_instructions.items():
            if isinstance(value, str):
                self.merge_from_str(config, value, key)
            elif isinstance(value, list):
                self.merge_from_list(config, value, key)
            elif isinstance(value, dict):
                self.merge_from_dict(config[key], value)
            else:
                raise NotImplementedError

    def merge_from_list(self, config, sources, key=None):
        for source in reversed(sources):
            if isinstance(source, str):
                self.merge_from_str(config, source, key=key)
            elif isinstance(source, list):
                self.merge_from_list(config, source)
            elif isinstance(source, dict):
                self.merge_from_dict(config, source)
            else:
                raise NotImplementedError

    def load(self) -> Dict[str, Any]:
        cls = type(self)
        config = cls.load_raw(self.raw_data)
        extends = config.pop(self.base_key, None)

        reference_data = {}
        if isinstance(extends, str):
            self.merge_from_str(reference_data, extends)
        elif isinstance(extends, dict):
            self.merge_from_dict(reference_data, extends)
        elif isinstance(extends, list):
            self.merge_from_list(reference_data, extends)
        elif extends:
            raise NotImplementedError

        full_merge(reference_data, config)
        return config
