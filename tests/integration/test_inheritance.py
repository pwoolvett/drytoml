import contextlib
import json
import tempfile
from pathlib import Path
from textwrap import dedent as _
from typing import Collection
from typing import Tuple

import pytest
from tests.paths import FIXTURES
from tests.utils import CustomEncoder

from drytoml.parser import Parser

EXAMPLE = FIXTURES / "example.toml"


@pytest.fixture()
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
        for name, __ in name_toml:
            toml_path = path / name
            parser = Parser.from_file(toml_path)
            document = parser.parse()
            tomls.append(document)
        yield tomls[0], tomls[-1]


def json_dumps(data: dict):
    return json.dumps(data, cls=CustomEncoder, sort_keys=True)


def assert_equal(result: dict, expected: dict):
    assert json_dumps(result) == json_dumps(expected)
    return True


def check(*toml_tuples):
    with setup_temp(toml_tuples) as (child_toml, expected_toml):
        assert_equal(child_toml, expected_toml)


def btest_full_toml_single_inheritance(example_raw):
    child = _(
        """\
        __extends = "parent.toml"
    """
    )
    parent = example_raw
    check(("child.toml", child), ("parent.toml", parent))


def btest_full_toml_disjoint_list_inheritance():
    child = _(
        """\
        __extends = ["table1.toml", "table2.toml"]
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


def btest_full_toml_intersect_list_inheritance():
    child = _(
        """\
        __extends = ["table1.toml", "table2.toml"]
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


def btest_full_toml_table_inheritance():
    child = _(
        """\
        [__extends]
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


def btest_table_inheritance():
    child = _(
        """\
        [from_table_1]
        __extends = "table1.toml"
        another = "value"
    """
    )
    table1 = _(
        """\
        [from_table_1]
        should_be_child = "table1"
        should_be_table1 = "table1"
        should_be_table2 = "table1"
    """
    )
    expected = _(
        """\
        [from_table_1]
        another = "value"
        should_be_child = "table1"
        should_be_table1 = "table1"
        should_be_table2 = "table1"
    """
    )
    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("expected.toml", expected),
    )


def btest_chained_table_inheritance():
    child = _(
        """\
        __extends = "table1.toml"
    """
    )
    table1 = _(
        """\
        [tool.black]
        __extends = "table2.toml"

        [tool.isort]
        __extends = "table3.toml"
    """
    )
    table2 = _(
        """\
        [tool.black]
        key1 = "value1"
        key2 = "value2"
    """
    )
    table3 = _(
        """\
        [tool.isort]
        key11 = "value11"
        key21 = "value21"
    """
    )
    expected = _(
        """\
        [tool.black]
        key1 = "value1"
        key2 = "value2"

        [tool.isort]
        key11 = "value11"
        key21 = "value21"
    """
    )
    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("table2.toml", table2),
        ("table3.toml", table3),
        ("expected.toml", expected),
    )


def test_github():
    child = _(
        """\
        __extends = "https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/pyproject.toml"

        [tool.other]
        section_key = "value"
    """
    )
    table1 = _(
        """\
[tool.black]
__extends = "https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/black.toml"

[tool.isort]
__extends = "https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/isort.toml"

[tool.docformatter]
__extends = "https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/docformatter.toml"

[tool.flakehell]
__extends = "https://raw.githubusercontent.com/rmclabs-io/dev-styleguide/main/python/flakehell.toml"
    """
    )
    expected = r"""[tool.other]
section_key = "value"

[tool.black]
line-length = 79
exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | data
  | \.tmp
  | \tmp
)/
'''



[tool.isort]
atomic = true
profile = "black"
known_local_folder = ["test"]
force_single_line = true
src_paths = ["src"]


[tool.docformatter]
blank = true
recursive = true


[tool.flakehell]
format = "colored"
docstring-convention = "google"  # flake8-docstrings
per-file-ignores = [
"tests/*.py: S101,D100,D101,D103,D104",  # tests without documentation, allow asserts
]
exclude = [
# self-managed files should not be checked
"poetry.lock",
"./.venv",
]
ignore = [
"F401", "E501"  # pylint takes care of these
]
max_line_length = 79
docstring_style = "google"  # darglint
[tool.flakehell.exceptions."tests/"]
flake8-docstrings = [
"-D100",
"-D101",
"-D102",
"-D103",
"-D104",
]
flake8-bandit = [
"-S101",  # asserts are ok
]
flake8-darglint = [
"-DAR101",
]
pylint = [
"-C0115",
"-C0115",
"-C0116",
"-C0116",
]

[tool.flakehell.plugins]
flake8-bandit = [
"+*",
"-S322",  # input for python2, no problem
]
flake8-bugbear = ["+*"]
flake8-builtins = ["+*"]
flake8-comprehensions = ["+*"]
flake8-darglint = ["+*"]
flake8-docstrings = [
"+*",
"-D202",  # black conflict
"-D412",  # we do want lines between header and contents. See https://github.com/PyCQA/pydocstyle/issues/412
]
flake8-eradicate = ["+*"]
flake8-isort = ["+*"]
flake8-debugger = ["+*"]
flake8-mutable = ["+*"]
flake8-pytest-style = ["+*"]
mccabe = ["+*"]
pep8-naming = [
"+*",
"-N805",  # pylint duplicate
]
pycodestyle = [
"+*",
"-E501",  # pylint duplicate
"-E203", # false positives on list slice
]
pyflakes = ["+*"]
pylint = ["+*"]
pandas-dev = ["+*"]"""

    check(
        ("child.toml", child),
        ("table1.toml", table1),
        ("expected.toml", expected),
    )
