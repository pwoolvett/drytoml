# -*- coding: utf-8 -*-
"""Custom types and synonyms."""
import re


class Url(str):
    """Avoid instantiation for non-compliant url strings."""

    URL_VALIDATOR = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # noqa: C0301  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    """Django validator."""

    def __init__(self, string):
        """Validate string as url before instantiating.

        Args:
            string: Url to validate

        Raises:
            ValueError: The received string is not a valid URL.
        """
        if not self.validate(string):
            raise ValueError("Not a valid URL")
        super().__init__()

    @classmethod
    def validate(
        cls,
        maybe_url,
    ) -> bool:
        """Validate url string using django regex.

        Args:
            maybe_url: Url to validate.

        Returns:
            `True` iff validation succeeds.
        """
        return cls.URL_VALIDATOR.match(str(maybe_url)) is not None
