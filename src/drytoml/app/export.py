"""This module contains the `export` command and its required utilities."""
import logging

from drytoml.parser import DEFAULT_EXTEND_KEY
from drytoml.parser import Parser


def export(
    file="pyproject.toml",
    key=DEFAULT_EXTEND_KEY,
) -> str:
    """Generate resulting TOML after transclusion.

    Args:
        file: TOML file to transclude values.
        key: Name too look for inside the file to activate interpolation.

    Returns:
        The transcluded toml.

    Example:
        >>> toml = export("isort.toml", "base")
    """

    logging.basicConfig(level=60, format="%(message)s", force=True)
    return Parser.from_file(file, extend_key=key).parse().as_string()
