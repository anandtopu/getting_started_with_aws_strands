"""Execute delivered notebooks into an ignored folder, preserving clean originals.

Run: uv run --group notebooks python scripts/check_notebooks.py
Expected: PASS for each delivered notebook. Cost: $0; all lesson calls use mocks.
AWS resources: none. Jupyter uses local loopback; lessons block external traffic.
"""

import os
import sys

from common.config import ROOT


def main() -> int:
    try:
        import nbformat
        from jupyter_client import KernelManager
        from nbclient import NotebookClient
    except ImportError:
        print("Install notebook tools: uv sync --group notebooks")
        return 1

    output = ROOT / ".nimbus/executed_notebooks"
    output.mkdir(parents=True, exist_ok=True)
    os.environ["PYTHONUTF8"] = "1"
    paths = sorted((ROOT / "modules").glob("*/notebook.ipynb"))
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        manager = KernelManager(kernel_name="python3")
        manager.kernel_spec.argv = [
            sys.executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ]
        client = NotebookClient(
            notebook,
            km=manager,
            timeout=150,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        # Bind the kernel to this dependency environment, not a user's unrelated kernelspec.
        try:
            client.execute(env={**os.environ, "VIRTUAL_ENV": sys.prefix})
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
        nbformat.write(notebook, output / f"{path.parent.name}.ipynb")
        print(f"PASS {path.relative_to(ROOT)}", flush=True)
    print(f"Executed {len(paths)} notebooks; originals retain no outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
