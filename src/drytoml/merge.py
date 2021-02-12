# -*- coding: utf-8 -*-
"""Utilities and logic for handling inter-toml merges."""

from typing import Dict
from typing import List
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

from drytoml.locate import deep_del

RAW_ITEMS = (
    Integer,
    Float,
    Bool,
    DateTime,
    Date,
    Time,
    String,
    Null,
)


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

    if isinstance(current, RAW_ITEMS):
        if isinstance(incoming, RAW_ITEMS):
            return current

    raise NotImplementedError


def merge_targeted(
    document: Container,
    incoming: Container,
    breadcrumbs: List[Union[str, int]],
) -> TOMLDocument:
    """Merge specific path contents from an incoming contianer into another.

    Args:
        document: The container to store the merge result.
        incoming: The source of the incoming data.
        breadcrumbs: Location of the incoming contend.

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


class TomlMerger:
    """Encapsulate toml merging strategies and procedures."""

    def merge_simple(
        self,
        value: Item,
        breadcrumbs: List[Key],
    ):
        """Merge a value in a specific position of the container.

        Args:
            value: Incoming data to be merged.
            breadcrumbs: Location of the parent container for the
                incoming value merge.
        """
        incoming_parser = self.build_subparser(value)
        incoming = incoming_parser.parse()
        merge_targeted(self.container, incoming, breadcrumbs)

    def merge_list_like(
        self,
        values: List[Item],
        breadcrumbs: List[Key],
    ):
        """Merge sequence of values in a specific position of the container.

        Args:
            values: Incoming data to be merged one by one, in reversed order.
            breadcrumbs: Location of the parent container for the
                    incoming value merge.
        """
        for val in reversed(values):
            self.merge_simple(
                val,
                breadcrumbs,
            )

    def merge_dict_like(
        self,
        dct: Dict[Key, Item],
        breadcrumbs: List[Key],
    ):
        """Merge a dict-like object into a specific container position.

        Args:
            dct: The incoming data.
            breadcrumbs: Location of the parent container for the
                    incoming data merge.
        """
        for key, val in dct.items():
            self(
                val,
                [*breadcrumbs, key],
            )

    def __init__(
        self,
        container: Container,
        parser,
    ):
        """Construct a merger which can transclude a TOML.

        Args:
            container: The outermost data container.
            parser: The parsed to be used for child parsed when
                transcluding toml objects.

        """
        self.container = container
        self.parser = parser

        strategies = {
            self.merge_simple: RAW_ITEMS,
            self.merge_list_like: (AoT, Array),
            self.merge_dict_like: (dict,),
        }
        self.merge_options = {
            item_type: solver
            for solver, item_types in strategies.items()
            for item_type in item_types
        }

    def build_subparser(self, value: Item):
        """Construct child parser from specific content.

        Args:
            value:The content of the TOML data to be parsed.

        Returns:
            The instantiated child parser.
        """

        return type(self.parser).factory(
            value,
            self.parser.extend_key,
            self.parser.reference,
            level=self.parser.level + 1,
        )

    def __call__(
        self,
        value: Item,
        breadcrumbs: List[Key],
        delete_dangling: bool = False,
    ):
        """Run the merging strategies.

        Args:
            value: Incoming value to merge into `self.container`.
            breadcrumbs: Location of the `base_key` which triggers the
                merge.
            delete_dangling: If set, removes the predefined base key
                which triggered the transclusions after merge is
                complete.

        Raises:
            NotImplementedError: Unable to merge given value type.
        """
        extend_key = self.parser.extend_key

        incoming_class = type(value)
        try:
            merge = self.merge_options[incoming_class]
        except KeyError as exc:
            raise NotImplementedError(
                "Unable to merge {} into {}".format(
                    incoming_class, type(self.container)
                )
            ) from exc

        merge(value, breadcrumbs)

        if delete_dangling:
            deep_del(self.container, extend_key, *breadcrumbs)
