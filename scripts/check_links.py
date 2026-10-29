"""Check Markdown file links offline; --external also checks public HTTP links.

Run: uv run python scripts/check_links.py
Expected: checked link count, zero failures. Cost: $0. AWS resources: none.
"""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx

from common.config import ROOT


def markdown_files() -> list[Path]:
    paths = [p for p in ROOT.glob("*.md")]
    for folder in (
        "docs",
        "data",
        "modules",
        "capstones",
        "infra",
        "checkpoints",
        "cheatsheets",
        ".github",
    ):
        paths.extend((ROOT / folder).rglob("*.md"))
    return sorted(set(paths))


def collect_links() -> tuple[list[str], set[str], int]:
    failures, external = [], set()
    count = 0
    for source in markdown_files():
        text = re.sub(r"```.*?```", "", source.read_text(encoding="utf-8"), flags=re.S)
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = match.group(1).strip().strip("<>")
            if target.startswith(("mailto:", "#")):
                continue
            count += 1
            if target.startswith(("https://", "http://")):
                external.add(target)
                continue
            path_part, _, anchor = target.partition("#")
            resolved = (source.parent / unquote(path_part)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                failures.append(f"{source.relative_to(ROOT)} -> {target}")
            elif anchor and resolved.suffix == ".md":
                headings = re.findall(
                    r"^#+\s+(.+)$", resolved.read_text(encoding="utf-8"), flags=re.M
                )
                slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
                if anchor not in slugs:
                    failures.append(f"{source.relative_to(ROOT)} -> missing anchor {target}")
    return failures, external, count


def check_external(url: str) -> str | None:
    # Prevent accidental checks against local endpoints in a public-doc link job.
    host = urlsplit(url).hostname or ""
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".invalid"):
        return None
    try:
        with httpx.Client(follow_redirects=True, timeout=20) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
    except httpx.HTTPError as exc:
        return f"{url}: {type(exc).__name__}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", action="store_true")
    args = parser.parse_args()
    failures, external, count = collect_links()
    if args.external:
        with ThreadPoolExecutor(max_workers=8) as pool:
            failures.extend(
                result for result in pool.map(check_external, sorted(external)) if result
            )
    for failure in failures:
        print(failure)
    print(f"Checked {count} links; {len(failures)} failures. External requests: {args.external}.")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
