"""Execute a delivered Python example with external network calls blocked."""

import runpy
import sys
from pathlib import Path

from common.config import ROOT
from common.network import offline_network


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/offline_run.py SCRIPT [arguments]")
    script = Path(sys.argv[1]).resolve()
    if not script.is_relative_to(ROOT) or not script.is_file():
        raise SystemExit("Choose an existing script inside this repository.")
    sys.argv = sys.argv[1:]
    with offline_network():
        runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
