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

   A: Use the `--key` flag (when using `dry` form cli, or initialize
   `drytoml.parser.Parser` using the `extend_key` kwarg.


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
     run inside the virtual environment.

   * Using poetry: `poetry install -E dev`

   * Using pip (>20 recommended): `pip install .[dev]`

   The next steps assume you have already activated the venv.

1. Install pre-commit hook (skip if using devcontainer)

   ```console
   pre-commit install --hook-type commit-msg
   ```

   * Commits in every branch except those starting with `wip/` must be compliant to
     [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

   * Commit using `cz` to ensure compliance.

1. Add tests to code

1. Run check(s)


   Useful tip: To debug your code, a useful tool is using `drytoml -v explain`

   * Manually, executing the check from inside a venv

     For example, to generate the documentation:
  
     ```console
     sphinx-apidoc \
       --templatedir=docs/src/templates \
       --separate \
       --module-first \
       --force \
       -o docs/src/apidoc src/drytoml
     ```

     and then

     ```console
     sphinx-build docs/src docs/build
     ```

      See the different checks in `.github/workflows`

   * Locally with [act](https://github.com/nektos/act) (Already installed in the
     devcontainer)

     For example, to emulate a PR run for the docs workflow:
  
     ```console
     act -W .github/workflows/docs.yml pull_request
     ```

   * Remotely, by pushing to an open PR




1. Create PR

## TODO

check out current development [here](https://github.com/pwoolvett/drytoml/projects/2)
