import json
import re
import tempfile
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, MutableMapping, Optional, Union

import toml
from drytoml.merge import full_merge, merge
from drytoml.utils import (Cached, Url, find_recursive, getitem_deep, is_url,
                           request, sortOD)


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
        self._dict: dict = None

    @property
    def raw_data(self) -> str:
        """Read the string from the source"""
        if self._data:
            return self._data

        if Path(self.source).exists():
            with open(self.source) as fp:
                self._data = fp.read()
        elif is_url(self.source):
            self._data = request(str(self.source))
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


    def merge_section_from_str(self, config, source, *keys):
        reference_toml = self.build_child(source).load()
        reference_data = getitem_deep(reference_toml, *keys)
        full_merge(reference_data, config)
        print(config)


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

    def merge_toplevel(self, extends, config):
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

    def merge_sections(self, config):
        base_key_locations = sorted(
            find_recursive(self.base_key, config),
            key=lambda path_ct: path_ct[0]
        )

        for path, content in base_key_locations:
            config2 = getitem_deep(config, *path)
            extends = config2.pop(self.base_key, None)
            self.merge_from_str(config, content, path)
            # self.merge_section_from_str(config2, content, *path)
            # self.merge_toplevel(extends, config2)

    def load(self) -> MutableMapping[str, Any]:
        cls = type(self)

        config = cls.load_raw(self.raw_data)
        self.merge_toplevel(config.pop(self.base_key, None), config)

        self.merge_sections(config)
        self._dict = config
        return config

    def as_dict(self):
        if not self._dict:
            self.load()
        return self._dict

    @contextmanager
    def virtual(self):
        raw_data = self.as_dict()
        tidy = sortOD(raw_data)
        with tempfile.NamedTemporaryFile(
            mode='w+',
            suffix=".toml",
            prefix="drytoml.black",
        ) as fp:

            fp.write(toml.dumps(tidy))
            fp.seek(0)
            yield fp
