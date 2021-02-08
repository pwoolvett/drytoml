import contextlib
import json
import tempfile
from pathlib import Path
from textwrap import dedent as _
from typing import Collection
from typing import Tuple

import pytest
import toml
from drytoml.reader import Toml
from tests.paths import FIXTURES
from tests.utils import CustomEncoder

EXAMPLE = FIXTURES / "example.toml"


@pytest.fixture
def example_raw():
    with open(EXAMPLE) as fp:
        return fp.read()


@contextlib.contextmanager
def setup_temp(name_toml: Collection[Tuple[str, str]]):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        tomls = []
        for name, raw in name_toml:
            toml_path = path / name
            with open(toml_path, "w") as fp:
                fp.write(raw)
        # iterate twice here to ensure files exist for relative
        # referencing. Alternatively, we could ensure iteration goes
        # through parents, then through children...
        for name, raw in name_toml:
            toml_path = path / name
            tomls.append(Toml(toml_path).load())
        yield tomls[0], tomls[-1]


def json_dumps(data: dict):
    return json.dumps(data, cls=CustomEncoder, sort_keys=True)


def assertEqual(result: dict, expected: dict):
    assert json_dumps(result) == json_dumps(expected)
    return True


def check(*toml_tuples):
    with setup_temp(toml_tuples) as (child_toml, expected_toml):
        assertEqual(child_toml, expected_toml)


def test_full_toml_single_inheritance(example_raw):
    child = _(
        """\
        extends = "parent.toml"
    """
    )
    parent = example_raw
    check(("child.toml", child), ("parent.toml", parent))


def test_full_toml_disjoint_list_inheritance():
    child = _(
        """\
        extends = ["table1.toml", "table2.toml"]
    """
    )
    table1 = _(
        """\
        tabe1data = {foo = "bar"}
    """
    )
    table2 = _(
        """\
        tabe2data = {fizz = "buzz"}
    """
    )
    expected = _(
        """\
        [tabe1data]
        foo = "bar"

        [tabe2data]
        fizz = "buzz"
    """
    )
    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("table2.toml", table2),
        ("expected.toml", expected),
    )


def test_full_toml_intersect_list_inheritance():
    child = _(
        """\
        extends = ["table1.toml", "table2.toml"]
        [child_only_section]
        should_be_child = "child"

        [common]
        should_be_child = "child"
    """
    )
    table1 = _(
        """\
        [common]
        should_be_child = "table1"
        should_be_table1 = "table1"
        should_be_table2 = "table1"
    """
    )
    table2 = _(
        """\
        [common]
        should_be_child = "table2"
        should_be_table2 = "table2"
    """
    )
    expected = _(
        """\
        [child_only_section]
        should_be_child = "child"

        [common]
        should_be_child = "child"
        should_be_table1 = "table1"
        should_be_table2 = "table2"
    """
    )
    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("table2.toml", table2),
        ("expected.toml", expected),
    )


def test_full_toml_table_inheritance():
    child = _(
        """\
        [extends]
        first_only = "table1.toml"
        second_only = "table2.toml"
        common = ["table1.toml", "table2.toml"]

        [child_only_section]
        should_be_child = "child"

        [common]
        should_be_child = "child"
    """
    )
    table1 = _(
        """\
        [common]
        should_be_child = "table1"
        should_be_table1 = "table1"
        should_be_table2 = "table1"

        [first_only]
        should_be_table1 = "table1"

        [second_only]
        should_be_table2 = "table1"
    """
    )
    table2 = _(
        """\
        [common]
        should_be_child = "table2"
        should_be_table2 = "table2"

        [first_only]
        should_be_table1 = "table2"

        [second_only]
        should_be_table2 = "table2"
    """
    )
    expected = _(
        """\
        [first_only]
        should_be_table1 = "table1"

        [second_only]
        should_be_table2 = "table2"

        [child_only_section]
        should_be_child = "child"

        [common]
        should_be_child = "child"
        should_be_table1 = "table1"
        should_be_table2 = "table2"
    """
    )
    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("table2.toml", table2),
        ("expected.toml", expected),
    )


# def test_single_table_full_inheritance():
#     raise NotImplementedError

# def test_single_table_extended_inheritance():
#     raise NotImplementedError

# def test_single_table_extended_inheritance():
#     raise NotImplementedError
