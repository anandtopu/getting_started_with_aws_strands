"""Check TypeScript types, exercise contracts and every finite offline example.

Run: uv run python scripts/check_typescript.py
First install Node.js 22+ and npm ci --prefix modules/bonus/B2_typescript.
Cost: $0. AWS resources: none; all model calls use the scripted SDK model.
"""

import shutil
import subprocess

from common.config import ROOT


def main() -> int:
    folder = ROOT / "modules/bonus/B2_typescript"
    npm, node = shutil.which("npm"), shutil.which("node")
    if not npm or not node or not (folder / "node_modules/tsx").exists():
        print("Install Node.js 22+ and npm ci --prefix modules/bonus/B2_typescript")
        return 1
    commands = [[npm, "run", "check"], [npm, "test"]]
    for path in sorted((folder / "examples").glob("*.ts")) + sorted(
        (folder / "use_case").glob("*.ts")
    ):
        commands.append([node, "--import", "tsx", str(path), "--mock"])
    for command in commands:
        subprocess.run(command, cwd=folder, check=True, timeout=90)
    print("TypeScript: types, tests and four offline scripts passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
