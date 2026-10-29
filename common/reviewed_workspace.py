"""A deliberately tiny teaching execution backend, not general code isolation.

Only two fixed snippets can execute. All file paths are virtual absolute paths
inside a disposable folder. Mutations/execution request consent. A real deployment
needs an OS/container boundary and application authorization as well.
"""

import asyncio
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from strands.sandbox.base import Sandbox
from strands.sandbox.types import ExecutionResult, FileInfo

APPROVED_CODE = "print(round(100 * 0.92, 2))"


class ReviewedWorkspace(Sandbox):
    def __init__(self, root: Path, consent: Callable[[str], str] = input):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.consent = consent

    def resolve(self, path: str) -> Path:
        if not path.startswith("/") or "\\" in path or ":" in path:
            raise ValueError("Use a virtual absolute path such as /notes.txt")
        result = (self.root / path.lstrip("/")).resolve()
        if not result.is_relative_to(self.root):
            raise PermissionError("Path outside the reviewed workspace")
        return result

    def approve(self, description: str) -> None:
        if self.consent(description + " [yes/no]: ").strip().lower() != "yes":
            raise PermissionError("Human declined the operation")

    async def execute_code_streaming(self, code, language, *, timeout=None, **kwargs):
        if code != APPROVED_CODE or language != "python3":
            raise PermissionError("Only the reviewed currency snippet is allowed")
        self.approve(code)
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-I", "-c", code],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=min(timeout or 5, 5),
            check=False,
        )
        yield ExecutionResult(result.returncode, result.stdout, result.stderr)

    async def execute_streaming(self, command, *, timeout=None, **kwargs):
        if command != "nimbus-status":
            raise PermissionError("Only nimbus-status is allowed")
        self.approve(command)
        # No shell interpolation. The sole command maps to a fixed, harmless operation.
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-I", "-c", "print('Nimbus workspace ready')"],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=min(timeout or 5, 5),
            check=False,
        )
        yield ExecutionResult(result.returncode, result.stdout, result.stderr)

    async def read_file(self, path, **kwargs):
        return self.resolve(path).read_bytes()

    async def write_file(self, path, content, **kwargs):
        destination = self.resolve(path)
        self.approve(f"Write {path}: {content[:120]!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    async def remove_file(self, path, **kwargs):
        destination = self.resolve(path)
        self.approve(f"Remove {path}")
        destination.unlink()

    async def list_files(self, path, **kwargs):
        return [
            FileInfo(p.name, p.is_dir(), p.stat().st_size) for p in self.resolve(path).iterdir()
        ]
