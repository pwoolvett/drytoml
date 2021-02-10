# drytoml

Keep toml configuration centralized and personalizable.

`drytoml` enables having `.toml` files referencing any content from another `.toml`
file. You can reference the whole file, a specific table, or in general anything
reachable by a sequence of `getitem` calls (eg `["tool", "poetry", "source", 0, "url"]`)

Inspired by `flakehell` and `nitpick`, drytoml main motivation is to have several
projects share a common, centralized configuration defining codestyles, but still
allowing granular control wherever is required.

IMPORTANT: if you want to manually control transclusions and modify files by hand, you
should use other tools, like [nitpick](https://pypi.org/project/nitpick/).

## Usage

`drytoml` has two main usages:

1. Use a file as a reference to create an transcluded one:

    ```toml
    # contents of pyproject.dry.toml
    ...
    [tool.black]
    __extends = "../../common/black.toml"
    target-version = ['py37']
    include = '\.pyi?$'
    include = '\.pyi?$'
    ...
    ```

    ```toml
    # contents of ../../common/black.toml
    [tool.black]
    line-length = 100
    ```

   ```console
   $ dry export --file=pyproject.dry.toml > pyproject.toml
   ```

    ```toml
    # contents of pyproject.toml
    [tool.black]
    line-length = 100
    target-version = ['py37']
    include = '\.pyi?$'
    ```

2. Use included wrappers, allowing you to use your current configuration

   Instead of this:

   ```console
   $ black .
   All done! ✨ 🍰 ✨
   14 files left unchanged.
   ```

   You would run this
   ```console
   $ dry black
   reformatted /path/to/cwd/file_with_potentially_long_lines.py
   reformatted /path/to/cwd/another_file_with_potentially_long_lines.py
   All done! ✨ 🍰 ✨
   2 files reformatted, 12 files left unchanged.
   ```


Transclusion works with relative/absolute paths and urls. Internally
`drytoml` uses [tomlkit](https://pypi.org/project/tomlkit/) to merge the
corresponding sections between the local and referenced `.toml`.


For the moment, the following wrappers are supported:

* [x] [black](https://github.com/psf/black)
* [x] [isort](https://pycqa.github.io/isort/)
* [x] [flakehell, flake8helled](https://github.com/life4/flakehell) *
* [ ] docformatter
* [ ] pytest

- NOTE: flakehell project was archived. This requires using a custom fork from
  [here](https://github.com/pwoolvett/flakehell)
- NOTE flakehell already implements similar funcionality, using a `base` key inside
  `[tool.flakehell]`

## Setup

    Install as usual, with `pip`, `poetry`, etc:

### Prerequisites

### Install

## Usage

## FAQ

**Q: I want to use a different key**

   A: Use the `--key` flag (when using `dry` form cli,
      or initialize `drytoml.parser.Parser` using the `extend_key` kwarg.


**Q: I changed a referenced toml upstream (eg in github) but still get the same result.**

   A: Run `dry cache clear --help` to see available options.

## Contribute

* Use the devcontainer, `act` command to run github actions locally
* install locally with pip `pip install .[dev]` or poetry `poetry install -E dev`


1. Create issue
1. clone
1. add tests
1. Run check locally with [act](https://github.com/nektos/act)
1. Create PR

## TODO

check out current development [here](https://github.com/pwoolvett/drytoml/projects/2)
