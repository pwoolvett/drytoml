from typing import Any, Dict, List, Union

from drytoml.utils import getitem_deep, setitem_deep


def merge(
    left: Dict[str, Any],
    right: Dict[str, Any],
    location: Union[str, List[str]],
):
    """Update current mapping with reference location."""

    if isinstance(location, str):
        path=[location]
    else:
        path=location

    try:
        left_data = getitem_deep(left, *path)
    except KeyError:
        return

    try:
        right_data = getitem_deep(right, *path)
    except KeyError:
        # no merge is necessary if only one contains data
        setitem_deep(
            right,
            left_data,
            left,
            *path,
        )
        return
    left_dtype = type(left_data)
    right_dtype = type(right_data)

    if left_dtype == list:
        if right_dtype == list:  # list list
            right[location] = [*left_data, *right_data]
            return
        if right_dtype == dict:
            raise ValueError(f"Cannot merge table with non-table.")  # list, dict
        right[location] = [*left_data, right_data]  # list, native
        return

    if left_dtype == dict:
        if right_dtype != dict:  # dict, native & dict, list
            raise ValueError(f"Cannot merge table with non-table.")
        for key in {*left_data.keys(), *right_data.keys()}:  # dict, dict
            merge(left_data, right_data, key)
        return

    if right_dtype == list:  # native, list
        right[location] = [left_data, *right_data]
        return
    if right_dtype == dict:  # native, dict
        raise ValueError(f"Cannot merge table with non-table.")

    right[location] = right_data
    return


def full_merge(
    left: Dict[str, Any],
    right: Dict[str, Any],
):
    for key in {*left.keys(), *right.keys()}:
        merge(left, right, key)
