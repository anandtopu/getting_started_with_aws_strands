"""Build a small allow-listed Docker context; never include credentials or the working tree.

Run: uv run python scripts/prepare_deployment.py
Expected: three context paths. Cost/resources: $0, local files only.
"""

import argparse
import shutil
from pathlib import Path

from common.config import ROOT

MODULES = (
    "__init__",
    "config",
    "models",
    "ollama_structured",
    "data",
    "testing",
    "pretty",
    "coordination",
    "production_support",
    "deployment_apps",
    "scheduled_evaluation",
    "flagship_runtime",
    "agentcore_identity",
    "agentcore_memory",
    "cloud_clients",
    "gateway_booking",
    "mcp_clients",
    "public_booking",
)


def clean_generated_context(path: Path) -> None:
    boundary = (ROOT / ".nimbus").resolve()
    target = path.resolve()
    if path.is_symlink() or target == boundary or not target.is_relative_to(boundary):
        raise ValueError("Generated contexts must stay inside the course scratch directory")
    path.mkdir(parents=True, exist_ok=True)
    # A fresh generated context avoids stale files accidentally entering a later build.
    for existing in path.iterdir():
        resolved = existing.resolve()
        if existing.is_symlink() or not resolved.is_relative_to(path.resolve()):
            raise ValueError("Unsafe deployment context entry")
        if existing.is_dir():
            shutil.rmtree(resolved)
        else:
            existing.unlink()


def prepare(kind: str) -> Path:
    if kind not in {"lambda", "runtime", "fargate"}:
        raise ValueError("Unknown hosting adapter")
    path = ROOT / ".nimbus/deploy-context" / kind
    clean_generated_context(path)
    for folder in ("common", "data/policies"):
        (path / folder).mkdir(parents=True, exist_ok=True)
    for name in MODULES:
        shutil.copyfile(ROOT / "common" / (name + ".py"), path / "common" / (name + ".py"))
    for policy in (ROOT / "data/policies").glob("*.md"):
        shutil.copyfile(policy, path / "data/policies" / policy.name)
    shutil.copyfile(ROOT / "data/flights.csv", path / "data/flights.csv")
    shutil.copyfile(ROOT / "deploy/requirements.txt", path / "requirements.txt")
    shutil.copyfile(ROOT / "deploy" / (kind + ".Dockerfile"), path / "Dockerfile")
    # No .env file is copied. AWS roles and explicit deployment environment supply settings.
    (path / ".env.example").write_text("BYPASS_TOOL_CONSENT=false\n", encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["lambda", "runtime", "fargate"])
    args = parser.parse_args()
    for kind in [args.kind] if args.kind else ["lambda", "runtime", "fargate"]:
        print(prepare(kind))


if __name__ == "__main__":
    main()
