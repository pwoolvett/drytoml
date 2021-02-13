# drytoml

Keep your toml configuration centralized and personalizable.


[![PyPI](https://img.shields.io/pypi/v/drytoml?color=yellow)](https://pypi.org/project/drytoml/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drytoml)](https://www.python.org/downloads/)

[![ReadTheDocs](https://readthedocs.org/projects/drytoml/badge/?version=latest)](https://drytoml.readthedocs.io/en/latest/)
[![Format](https://github.com/pwoolvett/drytoml/workflows/Format/badge.svg)](https://github.com/pwoolvett/drytoml/actions?query=workflow%3AFormat)
[![Lint](https://github.com/pwoolvett/drytoml/workflows/Lint/badge.svg)](https://github.com/pwoolvett/drytoml/actions?query=workflow%3ALint)
[![Test](https://github.com/pwoolvett/drytoml/workflows/Test/badge.svg)](https://github.com/pwoolvett/drytoml/actions?query=workflow%3ATest)


[![VSCode Ready-to-Code](https://img.shields.io/badge/devcontainer-enabled-blue?logo=docker)](https://code.visualstudio.com/docs/remote/containers)
[![License: Unlicense](https://img.shields.io/badge/license-UNLICENSE-white.svg)](http://unlicense.org/)


---


Through `drytoml`, TOML files can have references to any content from another TOML file.
References work with relative/absolute paths and urls, and can point to whole files, a
specific table, or in general anything reachable by a sequence of `getitem` calls, like
`["tool", "poetry", "source", 0, "url"]`. `drytoml` takes care of transcluding the
content for you.

Inspired by `flakehell` and `nitpick`, the main motivation behind `drytoml` is to have
several projects sharing a common, centralized configuration defining codestyles, but
still allowing granular control when required.

This is a deliberate alternative to tools like [nitpick](https://pypi.org/project/nitpick/),
which works as a linter instead, ensuring your local files have the right content.


## Usage

`drytoml` has two main usages:

1. Use a file as a reference and "build" the resulting one:

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

2. Use included wrappers, allowing you to use references in your current configuration
   without changing any file:

   For a given code structure and the sample `pyproject.toml` in the previous example,
   instead of this:

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

   What just happened? `drytoml` comes with a set of wrappers which (1) create a
   transcluded temporary file, (2) configure the wrapped tool to use said file, and (3)
   get rid of the file after running the tool.


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
- `drytoml` uses [tomlkit](https://pypi.org/project/tomlkit/) internally to merge the 
  corresponding sections between the local and referenced `.toml`.

## Setup

### Prerequisites

  * A compatible python >3.6.9
  * [recommended] virtualenv
  * A recen `pip`

### Install

  Install as usual, with `pip`, `poetry`, etc:

* `pip install drytoml`
* `poetry add drytoml` (probably you'll want `poetry add --dev drytoml` instead)

## Usage

For any command , run `--help` to find out flags and usage.
Most common:

* Use any of the provided wrappers as a subcommand, eg `dry black` instead of `black`.
* Use `dry -q export` and redirect to a file, to generate a new file with transcluded
  contents
* Use `dry cache` to manage the cache for remote references.



## FAQ

**Q: I want to use a different key to trigger transclusions**

   A: In cli mode (using the `dry` command), you can pass the `--key` flagcli, to change
      it. In api mode (from python code), initialize `drytoml.parser.Parser` using a
      custom value for the `extend_key` kwarg.


**Q: I changed a referenced toml upstream (eg in github) but still get the same result.**

   A: Run `dry cache clear --help` to see available options.

## Contribute

* Use the devcontainer, `act` command to run github actions locally
* install locally with pip `pip install .[dev]` or poetry `poetry install -E dev`


1. Create issue

1. clone

1. Setup Dev environment

   * The easiest way is to use the provided devcontainer inside vscode, which already
     contains everything pre-installed. You must open the cloned directory using the
     [remote-containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
     Just run `poetry shell` or prepend any command with `poetry run` to ensure commands
     are run inside the virtual environment.

   * Using poetry: `poetry install -E dev`

   * Using pip (>20 recommended): `pip install .[dev]`

   The next steps assume you have already activated the venv.

1. Commiting

   * Commits in every branch except those starting with `wip/` must be compliant to
     [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Releases
     are done automatically and require commit messages compliance.

   * To validate commits, you can install the pre-commit hook

     ```console
     pre-commit install --hook-type commit-msg
     ```

   * With venv activated, you can commit using `cz commit` instead of `git commit`
     to ensure compliance.

1. Add tests to code

1. Run check(s)


   * To debug your code, `drytoml -v explain` helps a lot to trace the parser.
   * See the different checks in `.github/workflows`

   There are three ways to check your code:

   * Manually, executing the check from inside a venv

     For example, to generate the documentation, check `.github/workflows/docs`. To run
     the `Build with Sphinx` step:

     ```console
     sphinx-build docs/src docs/build
     ```

     Or to run pytest, from `.github/workflows/tests.yml`:

     ```console
     sphinx-build docs/src docs/build
     ```

     ... etc

   * Locally, with [act](https://github.com/nektos/act) (Already installed in the
     devcontainer)

     For example, to emulate a PR run for the docs workflow:
  
     ```console
     act -W .github/workflows/docs.yml pull_request
     ```

   * Remotely, by pushing to an open PR

1. Create PR

## TODO

Check out current development [here](https://github.com/pwoolvett/drytoml/projects/2)
