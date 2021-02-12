# -*- coding: utf-8 -*-
"""Additional Source to transclude tomlkit with URL and files."""

from pathlib import Path
from textwrap import dedent as _
from typing import Optional
from typing import Union

from tomlkit.parser import Parser as BaseParser

from drytoml import logger
from drytoml.types import Url
from drytoml.utils import deep_del
from drytoml.utils import deep_find
from drytoml.utils import merge_from_value
from drytoml.utils import request

DEFAULT_EXTEND_KEY = "__extends"


class Parser(BaseParser):
    """Extend tomlkit parser to allow transclusion."""

    def __init__(
        self,
        string: str,
        extend_key=DEFAULT_EXTEND_KEY,
        reference: Optional[Union[str, Path, Url]] = None,
        level=0,
    ):
        """Construct a transclusion-enabled toml parser.

        Args:
            string: Raw toml content.
            extend_key: key to look for to init transclusion.
            reference: Reference for the source of the content
                (eg url, file, etc).
            level: Number of parent documents previously parsed to
                instantiate this.
        """
        self.extend_key = extend_key
        self.reference = reference or Path.cwd()
        self.from_string = not reference
        self.level = level
        super().__init__(string)

    def __repr__(self):
        """Enable parser visual differentiation from repr.

        Examples:

        >>> parser = Parser.from_file("pyproject.toml")
        >>> parser
        Parser('pyproject.toml', extend_key='__extends')

        >>> content = parser.parse().as_string()
        >>> Parser(content)
        Parser('/path/to/dir' as cwd, (from string), extend_key='__extends')

        >>> Parser.factory("https://github.com/pytest-dev/pytest/blob/master/pyproject.toml")
        Parser('https://github.com/pytest-dev/pytest/blob/master/pyproject.toml', extend_key='__extends')
        """
        return "{}Parser('{}'{}, extend_key='{}')".format(
            self._log_indent,
            self.reference,
            " as cwd, (from string)" if self.from_string else "",
            self.extend_key,
        )

    @classmethod
    def from_file(cls, path, extend_key=DEFAULT_EXTEND_KEY, level=0):
        """Instantiate a parser from file.

        Args:
            path: Path to an existing file with the toml contents.
            extend_key: kwarg to construct the parser.
            level: kwarg to construct the parser.
        """
        with open(path) as fp:
            raw = fp.read()
        return cls(raw, extend_key=extend_key, reference=path, level=level)

    @classmethod
    def from_url(cls, url, extend_key=DEFAULT_EXTEND_KEY, level=0):
        """Instantiate a parser from url.

        Args:
            url: URL to an existing file with the toml contents.
            extend_key: kwarg to construct the parser.
            level: kwarg to construct the parser.
        """
        raw = request(url)
        return cls(raw, extend_key=extend_key, reference=url, level=level)

    @classmethod
    def factory(
        cls,
        reference: Union[str, Url, Path],
        extend_key=DEFAULT_EXTEND_KEY,
        parent_reference: Optional[Union[str, Path, Url]] = None,
        level=0,
    ):
        """Instantiate a parser from url, string, or path.

        Args:
            reference: Existing file/url/path with the toml contents.
            extend_key: kwarg to construct the parser.
            parent_reference: Used to parse relative paths.
            level: kwarg to construct the parser.
        """

        if Url.validate(reference):
            return cls.from_url(
                reference,
                extend_key=extend_key,
                level=level,
            )

        path = Path(reference)
        if not path.is_absolute():
            if not parent_reference:
                raise ValueError("Must supply absolute path or parent")
            path = (parent_reference.parent / path).resolve()

        return cls.from_file(path, extend_key=extend_key, level=level)

    @property
    def _log_indent(self):
        return " " * 2 * self.level

    def _log_document(self, document):
        raw = document.as_string()
        return _(
            f"""
{"="*30}{self} CONTENTS STARTS HERE{"="*30}
{raw}
{"="*30}{self} CONTENTS END HERE{"="*30}"""
        ).replace("\n", f"\n{self._log_indent}")

    def parse(self):
        """Parse recursively until no transclusions are required."""
        document = super().parse()
        logger.info(f"{self}: Parsing started")
        logger.debug(
            "{}: Source contents:\n\n{}".format(
                self, self._log_document(document)
            )
        )

        while True:
            base_key_locations = sorted(
                deep_find(document, self.extend_key),
                key=lambda path_ct: path_ct[0],
            )

            if not base_key_locations:
                logger.debug(f"{self}: No {self.extend_key} found")
                break
            logger.info(
                "{}: Found '{}': at {}".format(
                    self,
                    self.extend_key,
                    [
                        ".".join(crumbs_val[0]) or "(document root)"
                        for crumbs_val in base_key_locations
                    ],
                )
            )

            for breadcrumbs, value in base_key_locations:
                logger.debug(
                    "{}: Before merging {} contents:\n\n{}".format(
                        self, breadcrumbs, self._log_document(document)
                    )
                )
                merge_from_value(
                    value,
                    document,
                    breadcrumbs,
                    self.extend_key,
                    type(self),
                    self.reference,
                    self.level + 1,
                )
                deep_del(document, self.extend_key, *breadcrumbs)
                logger.debug(
                    "{}: After merging {} contents:\n\n{}".format(
                        self, breadcrumbs, self._log_document(document)
                    )
                )

        logger.info(f"{self}: Parsing finished")
        logger.debug(
            "{}: Final contents:\n\n{}".format(
                self, self._log_document(document)
            )
        )
        return document
