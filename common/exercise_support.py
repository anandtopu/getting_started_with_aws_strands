"""Load numbered lesson files without treating their directories as Python packages."""

import importlib.util
import json

from common.config import ROOT


def load_exercise(slug: str, folder: str, filename: str):
    path = (ROOT / "modules" / slug / folder / filename).resolve()
    if not path.is_relative_to(ROOT / "modules"):
        raise ValueError("Exercise path outside modules")
    spec = importlib.util.spec_from_file_location(f"{slug}_{folder}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exercise_cases(slug: str) -> list[tuple]:
    data = [
        row
        for path in sorted((ROOT / "docs/verification").glob("tier*_exercises.json"))
        for row in json.loads(path.read_text(encoding="utf-8"))
    ]
    record = next(row for row in data if row["module"] == slug)
    return [
        (exercise["file"], case["input"], case["expected"])
        for exercise in record["exercises"]
        for case in exercise["cases"]
    ]
