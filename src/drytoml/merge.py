from typing import Any
from typing import Dict


def merge(
    left: Dict[str, Any],
    right: Dict[str, Any],
    location: str,
):
    """Update current mapping with reference location."""

    if location not in left:
        return

    left_data = left[location]

    # no merge is necessary if only one contains data
    if location not in right:
        right[location] = left_data
        return

    right_data = right[location]

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
