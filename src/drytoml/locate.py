# -*- coding: utf-8 -*-
"""Utilities to simplify deep `getitem` calls."""

from typing import Generator
from typing import List
from typing import Optional
from typing import Union

from tomlkit.items import Key


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
