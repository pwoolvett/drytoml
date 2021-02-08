import re

from typing import Any
from typing import List
from typing import Tuple
from typing import Union

class Cached(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = f"{cls.__name__}-{repr(args)}-{repr(kwargs)}"
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]


Url = str

URL_VALIDATOR = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)
"""Django validator."""


def is_url(maybe_url):
    return URL_VALIDATOR.match(str(maybe_url)) is not None

def find_recursive(
    key:str,
    container: Union[str, list, dict],
    path=None
):
    path = path or []

    if isinstance(container, list):
        for index, element in enumerate(container):
            yield from find_recursive(key, element, [*path, index])
        return list

    if isinstance(container, dict):
        for name, content in container.items():
            yield from find_recursive(key, content, [*path, name])

            if name == key:
                yield path, content

        return dict

    return type(container)
