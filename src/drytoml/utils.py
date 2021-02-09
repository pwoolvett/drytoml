# -*- coding: utf-8 -*-
""""""

import functools
import hashlib
import re
import urllib.request
from logging import root as logger
from typing import List
from typing import Union

from drytoml.paths import CACHE
from drytoml.types import Url

from tomlkit.container import _NOT_SET
from tomlkit.container import Container
from tomlkit.items import Item

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


def cached(func):
    @functools.wraps(func)
    def wrapped(url: Url, *a, **kw):
        key = hashlib.sha1(url.encode("utf8")).hexdigest()
        path = CACHE / key
        if path.exists():
            logger.warning(
                f"DryToml: Using cached version of {url} from {path}"
            )
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


def deep_find(
    container: Union[
        str,
        list,
        dict,
    ],
    extend_key: str,
    breadcrumbs=None,
):
    breadcrumbs = breadcrumbs or []

    if isinstance(
        container,
        list,
    ):
        for index, element in enumerate(container):
            yield from deep_find(element, extend_key, [*breadcrumbs, index])
        return list

    if isinstance(
        container,
        dict,
    ):
        for name, content in container.items():
            yield from deep_find(content, extend_key, [*breadcrumbs, name])

            if name == extend_key:
                yield breadcrumbs, content

        return dict

    return type(container)


def deep_pop(document, breadcrumbs, default=_NOT_SET):
    crumbs, final = breadcrumbs[:-1], breadcrumbs[-1]
    current = document
    for key in crumbs:
        current = current[key]
    return current.pop(final, default)

def deep_del(document, final, *breadcrumbs):
    current = document
    for key in breadcrumbs:
        current = current[key]
    del current[final]

def deep_extend(current, incoming):
    current.extend(incoming)
    return current

def deep_merge(
    current,
    incoming
):
    if isinstance(current, list):
        if isinstance(incoming, list):
            return deep_extend(current, incoming)

    if isinstance(current, dict):
        if isinstance(incoming, dict):
            for key in {*current.keys(), *incoming.keys()}:
                if key not in incoming:
                    continue
                if key not in current:
                    # emulate incoming container skeleton
                    current[key] = incoming[key]
                    continue
                current[key] = deep_merge(current[key], incoming[key])
            return current
    if isinstance(current, str):
        if isinstance(incoming, str):
            return incoming

    raise NotImplementedError

def merge_targeted(
    document: Container,
    incoming: Container,
    breadcrumbs: List[Union[str, int]],
    value: Item,
):

    if not breadcrumbs:
        return deep_merge(document, incoming)

    location = document
    incoming_data = incoming
    crumbs, final = breadcrumbs[:-1], breadcrumbs[-1]

    for key in crumbs:
        incoming_data = incoming_data[key]
        if key not in location:
            # emulate incoming container skeleton
            location[key] = type(incoming_data)()
        location = location[key]

    location[final] = deep_merge(location[final], incoming_data[final])
    
    return document
