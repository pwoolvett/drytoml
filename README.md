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

check out current development [here](https://github.com/pwoolvett/drytoml/projects/2)
