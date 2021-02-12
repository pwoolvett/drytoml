import importlib
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import List

from drytoml.parser import Parser


def import_callable(string):
    module_str, tool_main_str = string.split(":")
    module = importlib.import_module(module_str)
    tool_main = getattr(module, tool_main_str)
    return tool_main


class Wrapper:
    cfg: str

    def __call__(self, importstr):
        with self.tmp_dump() as virtual:
            self.virtual = virtual
            self.pre_import()
            self.pre_call()
            tool_main = import_callable(importstr)
            sys.exit(tool_main())

    def pre_import(self):
        pass

    def pre_call(self):
        pass

    @contextmanager
    def tmp_dump(self):
        parser = Parser.from_file(self.cfg)
        document = parser.parse()

        # ensure locally referenced files work
        path = Path(self.cfg)
        if path.is_absolute():
            parent = path.parent
        else:
            parent = (Path.cwd() / self.cfg).parent

        with tempfile.NamedTemporaryFile(
            mode="w+",
            suffix=".toml",
            prefix="drytoml.",
            dir=str(parent),
        ) as fp:
            fp.write(document.as_string())
            fp.seek(0)
            yield fp


class Env(Wrapper):
    """Call another script, configuring it with an environment variable."""

    def __init__(self, env):
        self.env = env
        self.cfg = os.environ.get(env, "pyproject.toml")

    def pre_import(self):
        os.environ[self.env] = self.virtual.name


class Cli(Wrapper):
    """Call another script, configuring it with specific cli flag."""

    def __init__(self, configs:List[str]):
        """Instantiate a cli wrapper

        Args:
            configs: Possible names for the configuration flag of the
                wrapped script.
        """
        for option in configs:
            try:
                idx = sys.argv.index(option)
                pre = sys.argv[:idx]
                post = sys.argv[idx + 2 :]
                cfg = sys.argv[idx + 1]
                break
            except ValueError:
                pass
        else:
            pre = sys.argv
            post = []
            cfg = "pyproject.toml"
        self.cfg = cfg
        self.pre = pre
        self.post = post
        self.option = option

    def pre_call(self):
        sys.argv = [*self.pre, self.option, f"{self.virtual.name}", *self.post]


def black():
    """Execute black, configured with custom setting cli flag."""
    return Cli(["--config"])("black:patched_main")


def isort():
    """Execute isort, configured with custom setting cli flag."""
    return Cli(["--sp", "--settings-path", "--settings-file", "--settings"])(
        "isort.main:main"
    )


def flakehell():
    """Execute flakehell, configured with custom env var."""
    return Env("FLAKEHELL_TOML")("flakehell:entrypoint")


def flake8helled():
    """Execute flake8helled, configured with custom env var."""
    return Env("FLAKEHELL_TOML")("flakehell:flake8_entrypoint")
