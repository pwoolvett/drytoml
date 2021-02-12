# -*- coding: utf-8 -*-
"""Miscellaneous utilities used throughout the project."""

import functools
import hashlib
import urllib.request
from logging import root as logger
from typing import Union

from drytoml.paths import CACHE
from drytoml.types import Url


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
                "drytoml-cache: Using cached version of {} at {}",
                url,
                path,
            )
            with open(path) as fp:
                return fp.read()

        result = func(url, *a, **kw)
        logger.debug("Caching {url} into {path}", url, path)
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

    request_ = urllib.request.Request(Url(url))
    # avoid server-side caching
    request_.add_header("Pragma", "no-cache")
    request_.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(request_) as response:  # noqa: S310
        contents = response.read().decode("utf-8")
    return contents
