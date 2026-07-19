"""Allow `python -m scripts.external_sources run --source all`."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
