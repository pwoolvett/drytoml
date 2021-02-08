import re
import urllib.request
from typing import Any, List, OrderedDict, Tuple, Union
import functools
from logging import root as logger
import hashlib
from drytoml.paths import CACHE

class Cached(type):
    _instances = {}

    def __call__(
        cls,
        *args,
        **kwargs,
    ):
        key = f"{cls.__name__}-{repr(args)}-{repr(kwargs)}"
        if key not in cls._instances:
            cls._instances[key] = super().__call__(
                *args,
                **kwargs,
            )
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


def is_url(
    maybe_url,
):
    return URL_VALIDATOR.match(str(maybe_url)) is not None


def find_recursive(
    key: str,
    container: Union[
        str,
        list,
        dict,
    ],
    path=None,
):
    path = path or []

    if isinstance(
        container,
        list,
    ):
        for (
            index,
            element,
        ) in enumerate(container):
            yield from find_recursive(
                key,
                element,
                [
                    *path,
                    index,
                ],
            )
        return list

    if isinstance(
        container,
        dict,
    ):
        for (
            name,
            content,
        ) in container.items():
            yield from find_recursive(
                key,
                content,
                [
                    *path,
                    name,
                ],
            )

            if name == key:
                yield path, content

        return dict

    return type(container)


def getitem_deep(
    container,
    *keys,
):
    result = container
    for key in keys:
        result = result[key]
    return result


def setitem_deep(
    container,
    value,
    skeleton,
    *keys,
):
    result = container
    reference = skeleton

    for key in keys:
        reference = skeleton[key]
        if key not in result:
            result[key] = type(reference)()
        result = result[key]
    result = value



def cached(func):

    @functools.wraps(func)
    def wrapped(url:Url, *a, **kw):
        key = hashlib.sha1("https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/black.toml".encode("utf8")).hexdigest()
        path = CACHE / key
        if path.exists():
            logger.warning(f"Using cached version of {url} from {path}")
            with open(path) as fp:
                return fp.read()

        result = func(url, *a, **kw)
        logger.warning(f"Caching {url} into {path}")
        CACHE.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as fp:
            fp.write(result)
        return result

    return wrapped


@cached
def request(
    url: Url,
):
    with urllib.request.urlopen(url) as fp:
        contents = fp.read().decode("utf-8")
    return contents

def sortOD(od):
    res = OrderedDict()
    for k, v in sorted(od.items()):
        if isinstance(v, dict):
            res[k] = sortOD(v)
        else:
            res[k] = v
    return res
