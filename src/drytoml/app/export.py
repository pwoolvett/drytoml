from drytoml.parser import DEFAULT_EXTEND_KEY
from drytoml.parser import Parser


def export(
    file="pyproject.toml",
    key=DEFAULT_EXTEND_KEY,
):
    """Generate resulting TOML after transclusion.

    Args:
        file: TOML file to interpolate values.
        key: Name too look for inside the file to activate interpolation.

    Example:
        >>> toml = export("isort.toml", "base")
    """
    import logging

    logging.basicConfig(level=60, format="%(message)s", force=True)
    return Parser.from_file(file, extend_key=key).parse().as_string()
