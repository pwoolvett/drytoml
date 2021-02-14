"""Third-party commands enabled through drytoml."""

import importlib
import io
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable
from typing import List
from typing import Union

from drytoml.parser import Parser


def import_callable(string: str) -> Callable:
    """Import a module from a string using colon syntax.

    Args:
        string: String of the form `package.module:object`

    Returns:
        The imported module

    """
    module_str, tool_main_str = string.split(":")
    module = importlib.import_module(module_str)
    tool_main = getattr(module, tool_main_str)
    return tool_main


class Wrapper:
    """Common skeleton for third-party wrapper commands."""

    cfg: str
    virtual: io.StringIO

    def __call__(self, importstr):
        """Execute the wrapped callback.

        Args:
            importstr: String of the form `package.module:object`

        .. seealso:: `import_callable`

        """

        with self.tmp_dump() as virtual:
            self.virtual = virtual
            self.pre_import()
            self.pre_call()
            tool_main = import_callable(importstr)
            sys.exit(tool_main())

    def pre_import(self):
        """Execute custom processing done before callback import."""

    def pre_call(self):
        """Execute custom processing done before callback execut."""

    @contextmanager
    def tmp_dump(self):
        """Yield a temporary file with the configuration toml contents.

        Yields:
            Temporary file with the configuration toml contents
        """
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

    def __init__(self, env: Union[str, List[str]]):
        """Instantiate a cli wrapper.

        Args:
            env: Name(s) of the env var(s) to use which selects a
                 configuration file.
        """
        self.envs = (
            [
                env,
            ]
            if isinstance(env, str)
            else env
        )
        self.cfg = os.environ.get(self.envs[0], "pyproject.toml")

    def pre_import(self):
        """Configure env var before callback import."""
        for env in self.envs:
            os.environ[env] = self.virtual.name


class Cli(Wrapper):
    """Call another script, configuring it with specific cli flag."""

    def __init__(self, configs: List[str]):
        """Instantiate a cli wrapper.

        Args:
            configs: Possible names for the configuration flag of the
                wrapped script.

        Raises:
            ValueError: Empty configs.
        """
        if not configs:
            raise ValueError("No configuration strings received")

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
            option = configs[0]
        self.cfg = cfg
        self.pre = pre
        self.post = post
        self.option = option

    def pre_call(self) -> None:
        """Prepare sys.argv to contain the configuration flag and file."""
        sys.argv = [*self.pre, self.option, f"{self.virtual.name}", *self.post]


def black():
    """Execute black, configured with custom setting cli flag."""
    Cli(["--config"])("black:patched_main")


def isort():
    """Execute isort, configured with custom setting cli flag."""
    Cli(["--sp", "--settings-path", "--settings-file", "--settings"])(
        "isort.main:main"
    )


def pylint():
    """Execute pylint, configured with custom setting cli flag."""
    Cli(["--rcfile"])("pylint:run_pylint")


def flakehell():
    """Execute flakehell, configured with custom env var."""
    Env(["FLAKEHELL_TOML", "PYLINTRC"])("flakehell:entrypoint")


def flake8helled():
    """Execute flake8helled, configured with custom env var."""
    Env(["FLAKEHELL_TOML", "PYLINTRC"])("flakehell:flake8_entrypoint")
