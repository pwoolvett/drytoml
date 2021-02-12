"""Call drytoml's entrypoint as a python module.

Example:

    ```console
    $ python -m dry
    ```
"""
import sys

from drytoml.app import main

if __name__ == "__main__":
    sys.argv[0] = "dry"
    main()
