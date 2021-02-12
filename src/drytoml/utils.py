# -*- coding: utf-8 -*-
"""Miscellaneous utilities used throughout the project."""

import functools
import hashlib
import urllib.request
from logging import root as logger
from pathlib import Path
from typing import Generator
from typing import List
from typing import Optional
from typing import Union

from tomlkit.container import Container
from tomlkit.container import OutOfOrderTableProxy
from tomlkit.items import AoT
from tomlkit.items import Array
from tomlkit.items import Bool
from tomlkit.items import Date
from tomlkit.items import DateTime
from tomlkit.items import Float
from tomlkit.items import Integer
from tomlkit.items import Item
from tomlkit.items import Key
from tomlkit.items import Null
from tomlkit.items import String
from tomlkit.items import Table
from tomlkit.items import Time
from tomlkit.toml_document import TOMLDocument

from drytoml.paths import CACHE
from drytoml.types import Url

KEEP_CURRENT_IGNORE_INCOMING = (
    Integer,
    Float,
    Bool,
    DateTime,
    Date,
    Time,
    String,
    Null,
)


def cached(func):
    """Store output in drytoml's cache to use it on subsequent calls.

    Args:
        func: Function to decorate.

    Returns:
        Cached result with function result as fallback.

    .. seealso::

       * `drytoml.paths.CACHE`
       * `drytoml.app.cache`
    """

    @functools.wraps(func)
    def _wrapped(url: Url, *a, **kw):
        key = hashlib.sha256(url.encode("utf8")).hexdigest()
        path = CACHE / key
        if path.exists():
            logger.debug(
                f"drytoml-cache: Using cached version of {url} at {path}"
            )
            with open(path) as fp:
                return fp.read()

        result = func(url, *a, **kw)
        logger.debug(f"Caching {url} into {path}")
        CACHE.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as fp:
            fp.write(result)
        return result

    return _wrapped


@cached
def request(
    url: Union[str, Url],
) -> str:
    """Request a `url` using a GET.

    Args:
        url: The URL to GET.

    Returns:
        Decoded content.
    """
    with urllib.request.urlopen(  # noqa: S310
        urllib.request.Request(Url(url))
    ) as response:
        contents = response.read().decode("utf-8")
    return contents


def deep_find(
    container: Union[
        str,
        list,
        dict,
    ],
    extend_key: str,
    breadcrumbs: Optional[List[str]] = None,
) -> Generator[List[Key], type, None]:
    """Walk a data structure to yield all occurences of a key.

    Args:
        container: Where to look for the key.
        extend_key: The key to look for.
        breadcrumbs: The sequence of walked keys to the current position.

    Returns:
        The container type

    Yields:
        Tuple containing (`breadcrumbs`, `content`) where `extend_key`
            was found.

    """
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


def deep_del(document, final, *breadcrumbs):
    """Delete content located deep within a data structure.

    Args:
        document: Where to remove the content from.
        final: Last key required to locate the element to be deleted.
        breadcrumbs: The path to walk from the container root up to the
            parent ob the object to be deleted.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> container = {
        ...     "foo": [
        ...         {},
        ...         {"bar": "delete_me"}
        ...     ]
        ... }
        {'foo': [{}, {'bar': 'delete_me'}]}
        >>> deep_del(container, "bar", ["foo", 1])
        >>> container
        {'foo': [{}, {}]}
    """
    current = document
    for key in breadcrumbs:
        current = current[key]
    del current[final]


def deep_extend(
    current: Union[Array, AoT],
    incoming: Union[Array, AoT],
) -> Union[Array, AoT]:
    """Extend a container with another's contents.

    Args:
        current: Container to extend (in-place).
        incoming: Container to extend with.

    Returns:
        The recevied container, modified in-place.

    """
    current.extend(incoming)
    return current


def deep_merge(current: Item, incoming: Item) -> Item:
    """Merge two items using a type-dependent strategy.

    Args:
        current: Item to merge into.
        incoming: Item to merge from.

    Raises:
        NotImplementedError: Unable to merge received current and
            incoming item given their types.

    Returns:
        The current Item, after merging in-place.

    """

    if isinstance(current, list):
        if isinstance(incoming, list):
            return deep_extend(current, incoming)

    if isinstance(current, (Table, TOMLDocument, OutOfOrderTableProxy)):
        if isinstance(incoming, (Table, TOMLDocument, OutOfOrderTableProxy)):
            for key in {*current.keys(), *incoming.keys()}:
                if key not in incoming:
                    continue
                if key not in current:
                    # emulate incoming container skeleton
                    current.append(key, incoming[key])
                    continue
                current[key] = deep_merge(current[key], incoming[key])
            return current

    if isinstance(current, KEEP_CURRENT_IGNORE_INCOMING):
        if isinstance(incoming, KEEP_CURRENT_IGNORE_INCOMING):
            return current

    raise NotImplementedError


def merge_targeted(
    document: Container,
    incoming: Container,
    breadcrumbs: List[Union[str, int]],
    value: Item,
) -> TOMLDocument:
    """Merge specific path contents from an incoming contianer into another.

    Args:
        document: The container to store the merge result.
        incoming: The source of the incoming data.
        breadcrumbs: Location of the incoming contend.
        value: The actual content to be merged.

    Returns:
        The `document`, after merging in-place.
    """

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

    if final not in location:
        location[final] = incoming_data[final]
    else:
        location[final] = deep_merge(location[final], incoming_data[final])

    return document


def merge_from_value(
    value: Container,
    document: TOMLDocument,
    breadcrumbs: List[Key],
    extend_key: Key,
    cls,
    reference: Optional[Union[str, Path, Url]],
    level: int,
):
    """Store a dict-like object with an incoming data structure.

    Args:
        value: Value to merge.
        document:  The storage for the resulting merge.
        breadcrumbs: Keys to locate the extend_key
        extend_key: Final key to use when merging the two objects.
        cls: Parser class, used to instantiate children parsers.
        reference: The source of the current object, used to instantiate
            children parsers.
        level: The current parsing level, used to instantiate children
            parsers.

    Raises:
        NotImplementedError: Unable to merge given value type.

    """

    if isinstance(value, str):
        merge = merge_from_str
    elif isinstance(value, list):
        merge = merge_from_list
    elif isinstance(value, dict):
        merge = merge_from_dict
    else:
        raise NotImplementedError

    merge(
        value,
        document,
        breadcrumbs,
        extend_key,
        cls,
        reference,
        level,
    )


def merge_from_str(
    value,
    document,
    breadcrumbs,
    extend_key,
    cls,
    reference,
    level,
):
    """Store a dict-like object with an incoming value.

    Args:
        value: Incoming data to be merged.
        document: Storage for the resulting merge.
        breadcrumbs: Keys to locate the extend_key
        extend_key: Final key to use when merging the two objects.
        cls: Parser to use for sub-documents.
        reference: The source of the current object.
        level: The current parsing level, used to create new parsers.
    """
    incoming_parser = cls.factory(
        value,
        extend_key,
        reference,
        level=level,
    )
    incoming = incoming_parser.parse()
    merge_targeted(document, incoming, breadcrumbs, value)


def merge_from_list(
    values,
    document,
    breadcrumbs,
    extend_key,
    cls,
    reference,
    level,
):
    """Store a dict-like object with incoming values.

    Args:
        values: Incoming data to be merged one by one, in reversed order.
        document: Storage for the resulting merge.
        breadcrumbs: Keys to locate the extend_key
        extend_key: Final key to use when merging the two objects.
        cls: Parser to use for sub-documents.
        reference: The source of the current object.
        level: The current parsing level, used to create new parsers.
    """
    for val in reversed(values):
        merge_from_value(
            val,
            document,
            breadcrumbs,
            extend_key,
            cls,
            reference,
            level,
        )


def merge_from_dict(
    dct,
    document,
    breadcrumbs,
    extend_key,
    cls,
    reference,
    level,
):
    """Store a dict-like object with an incoming data structure.

    Args:
        dct: The original document, to be merged in-place.
        document:  The Storage for the resulting merge.
        breadcrumbs: Keys to locate the extend_key
        extend_key: Final key to use when merging the two objects.
        cls: Parser to use for sub-documents.
        reference: The source of the current object.
        level: The current parsing level, used to create new parsers.
    """
    for key, val in dct.items():
        merge_from_value(
            val,
            document,
            [*breadcrumbs, key],
            extend_key,
            cls,
            reference,
            level,
        )
