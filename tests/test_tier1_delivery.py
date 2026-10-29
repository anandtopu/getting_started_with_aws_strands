"""Keep delivered lessons runnable and distinguish them from future plans."""

import ast
import json

import pytest

from common.config import ROOT
from common.exercise_support import load_exercise

MODULES = sorted((ROOT / "modules").glob("[0-9][0-9]_*"))
EXERCISES = [
    path
    for module in MODULES
    for folder in ("exercises", "solutions")
    for path in (module / folder).glob("*.py")
]


@pytest.mark.parametrize("path", EXERCISES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_exercise_entrypoint_runs(path, capsys):
    module = load_exercise(path.parents[1].name, path.parent.name, path.name)
    module.main()
    assert capsys.readouterr().out.strip()


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_module_delivery_contract(module):
    guide = (module / "README.md").read_text(encoding="utf-8")
    for section in (
        "Prerequisites",
        "Learning objectives",
        "The big idea",
        "How it works",
        "Key APIs at a glance",
        "Walkthrough",
        "Real-world use case",
        "Common mistakes",
        "Exercises",
        "Quiz",
        "Key takeaways",
        "Go deeper",
        "Next:",
    ):
        assert f"## {section}" in guide
    assert "```mermaid" in guide
    assert 5 <= (module / "quiz.md").read_text(encoding="utf-8").count("<details>") <= 8
    assert len(list((module / "examples").glob("*.py"))) >= 3
    assert len(list((module / "use_case").glob("*.py"))) >= 1
    starters = sorted((module / "exercises").glob("*.py"))
    assert len(starters) == 3
    for path in starters:
        assert "# YOUR CODE HERE" in path.read_text(encoding="utf-8")
        assert (module / "solutions" / path.name).is_file()
    notebook = json.loads((module / "notebook.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    for path in [*(module / "examples").glob("*.py"), *(module / "use_case").glob("*.py")]:
        assert path.relative_to(ROOT).as_posix() in code


def test_manifest_covers_delivered_scripts_and_excludes_deprecated_tools():
    manifest = json.loads((ROOT / "scripts/examples_manifest.json").read_text())
    delivered = {entry["path"] for entry in manifest["examples"]}
    deprecated = {
        "calculator",
        "current_time",
        "http_request",
        "shell",
        "editor",
        "python_repl",
        "retrieve",
        "memory",
        "think",
        "journal",
        "use_llm",
    }
    for module in MODULES:
        for folder in ("examples", "use_case"):
            for path in (module / folder).glob("*.py"):
                assert path.relative_to(ROOT).as_posix() in delivered
                tree = ast.parse(path.read_text(encoding="utf-8"))
                assert ast.get_docstring(tree)
                assert any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module == "strands_tools":
                        assert not ({name.name for name in node.names} & deprecated), path
                    if isinstance(node, ast.ImportFrom) and node.module:
                        assert not any(
                            node.module.startswith(f"strands_tools.{name}") for name in deprecated
                        ), path
