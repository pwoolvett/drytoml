# -*- coding: utf-8 -*-
"""Additional Source to extend tomlkit with Urls"""

from pathlib import Path
from typing import Optional
from typing import Union

from drytoml.types import Url
from drytoml.utils import deep_find
from drytoml.utils import merge_targeted
from drytoml.utils import is_url
from drytoml.utils import request
from tomlkit.parser import Parser as BaseParser

DEFAULT_EXTEND_KEY = "__extends"


class Parser(BaseParser):
    def __init__(
        self,
        string: str,
        extend_key=DEFAULT_EXTEND_KEY,
        reference: Optional[Union[str, Path, Url]] = None,
    ):
        """"""
        self.extend_key = extend_key
        self.reference = reference or Path.cwd()
        super().__init__(string)

    @classmethod
    def from_file(cls, path, extend_key=DEFAULT_EXTEND_KEY):
        with open(path) as fp:
            raw = fp.read()
        return cls(raw, extend_key=extend_key, reference=path)

    @classmethod
    def from_url(cls, url, extend_key=DEFAULT_EXTEND_KEY):
        raw = request(url)
        return cls(raw, extend_key=extend_key, reference=url)

    @classmethod
    def factory(
        cls,
        reference: Union[str, Url, Path],
        extend_key=DEFAULT_EXTEND_KEY,
        parent_reference: Optional[Union[str, Path, Url]] = None,
    ):

        if is_url(reference):
            return cls.from_url(
                reference,
                extend_key=extend_key,
            )

        path = Path(reference)
        if not path.is_absolute():
            if not parent_reference:
                raise ValueError("Must supply absolute path or parent")
            path = (parent_reference.parent / path).resolve()

        return cls.from_file(path, extend_key=extend_key)

    def parse(self):
        document = super().parse()
        while True:
            base_key_locations = sorted(
                deep_find(document, self.extend_key),
                key=lambda path_ct: path_ct[0],
            )

            if not base_key_locations:
                break

            for breadcrumbs, value in base_key_locations:
                incoming_parser = type(self).factory(
                    value,
                    self.extend_key,
                    self.reference,
                )
                incoming = incoming_parser.parse()
                merge_targeted(document, incoming, breadcrumbs, value)
            

        return document
