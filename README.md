# drytoml

Keep toml configuration centralized and personalizable.

Inspired by `flakehell` and `nitpick`, drytoml aims at having a single, centralized
configuration for several project, as well as granular control on each table.

`drytoml` allows to have the following in your pyproject

```toml
...
[tool.black]
__extends = "../../common/black.toml"
...
```

It works with urls too, which is the main motivation for the project. Then, run `dry` followed by the executable. In this case:

```console
dry black
```

`drytoml` Uses [tomlkit]() and merges the corresponding sections between the local and referenced `toml`.


For the moment, the following providers are supported:

* [x] black
* [x] isort
* [ ] docformatter
* [ ] flakehell
* [ ] pytest



## Setup

### Prerequisites

### Install

## Usage

## Contribute

1. Create issue
1. clone
1. add tests
1. Create PR

## TODO

1. [ ] Add tests
1. [ ] Implement github actions
   1. [ ] matrix: 3.6, 3.9
   1. [ ] format
   1. [ ] lint
   1. [ ] pytest
   1. [ ] doc
   1. [ ] if tag publish to pypi
   1. [ ] if tag publish docs

1. [ ] Allow different key name from cli
1. [ ] Control verbosity from cli
1. [ ] Implement more providers
1. [ ] Use real cli framework (argparse is enough)
1. [ ] Implement show command
1. [ ] Update readme
1. [ ] Add tests
