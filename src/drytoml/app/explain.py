"""This module contains the `explain` command and its required utilities."""
from drytoml.parser import DEFAULT_EXTEND_KEY
from drytoml.parser import Parser


def explain(
    file="pyproject.toml",
    key=DEFAULT_EXTEND_KEY,
):
    """Show steps for toml transclusion.

    Args:
        file: TOML file to interpolate values.
        key: Name too look for inside the file to activate interpolation.

    Example:
        >>> explain("isort.toml", "base")
    """
    Parser.from_file(file, extend_key=key).parse()
