import sys

from drytoml.reader import Toml

def black():
    from black import patched_main
    try:
        idx = sys.argv.index("--config")
        pre = sys.argv[:idx]
        post = sys.argv[idx+2:]
        cfg = sys.argv[idx+1]
    except ValueError:
        pre = sys.argv
        post = []
        cfg = "pyproject.toml"

    merged = Toml(cfg)

    with merged.virtual() as virtual:
        sys.argv = [*pre, "--config", f"{virtual.name}", *post]
        print(sys.argv)
        import pdb;pdb.set_trace()
        patched_main()
