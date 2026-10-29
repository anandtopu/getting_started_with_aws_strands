"""Fail on unsafe samples, wildcard IAM actions and broken delivered file links."""

import ast
import json
import os
import re
from pathlib import Path

from dotenv import dotenv_values

from common.config import ROOT
from scripts.check_links import collect_links

SKIP = {".git", ".venv", ".nimbus", "tmp", "node_modules", "__pycache__"}


def repository_files():
    for folder, directories, names in os.walk(ROOT):
        directories[:] = [d for d in directories if d not in SKIP and not d.endswith(".egg-info")]
        for name in names:
            yield Path(folder) / name


def assert_narrow(actions, location):
    actions = [actions] if isinstance(actions, str) else actions
    assert isinstance(actions, list), f"IAM actions need a reviewable literal at {location}"
    assert all(isinstance(a, str) and not any(c in a for c in "*?") for a in actions), location


def walk_policy(value, location):
    if isinstance(value, dict):
        if "Effect" in value and ("Action" in value or "NotAction" in value):
            assert "NotAction" not in value, f"Broad NotAction needs explicit review: {location}"
            assert_narrow(value["Action"], location)
        for child in value.values():
            walk_policy(child, location)
    elif isinstance(value, list):
        for child in value:
            walk_policy(child, location)


def test_repo_wide_iam_actions_are_explicit():
    """Check JSON (including cdk.out), YAML and Python policy literals/constructs.

    There are no approved wildcard-action exceptions. Introduce one only with a
    reviewed rationale, a narrowly matched exception and a regression test here.
    Dynamic CDK policies must also be inspected after synth, before deployment.
    """
    import yaml

    for path in repository_files():
        if path.suffix == ".json":
            walk_policy(json.loads(path.read_text(encoding="utf-8")), path)
        elif path.suffix in {".yaml", ".yml"}:
            walk_policy(yaml.safe_load(path.read_text(encoding="utf-8")), path)
        elif path.suffix == ".py":
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Dict):
                    pairs = {
                        k.value: v
                        for k, v in zip(node.keys, node.values, strict=True)
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)
                    }
                    if "Effect" in pairs and "Action" in pairs:
                        assert_narrow(ast.literal_eval(pairs["Action"]), path)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "PolicyStatement":
                        for keyword in node.keywords:
                            if keyword.arg == "actions":
                                assert_narrow(ast.literal_eval(keyword.value), path)


def test_environment_sample_has_no_credentials_or_consent_bypass():
    path = ROOT / ".env.example"
    settings = dotenv_values(path, interpolate=False)
    for name, value in settings.items():
        if name != "MODEL_MAX_TOKENS" and any(
            word in name for word in ("API_KEY", "SECRET", "TOKEN", "PASSWORD", "ACCESS_KEY")
        ):
            assert not value, f"Credential-like value in {name}"
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"(?:AKIA|ASIA)[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{20,}", text)
    assert settings["BYPASS_TOOL_CONSENT"].lower() == "false"


def test_delivered_markdown_links_exist():
    failures, _, count = collect_links()
    assert count > 50
    assert failures == []


def test_notebooks_have_no_saved_outputs():
    for path in repository_files():
        if path.suffix == ".ipynb":
            notebook = json.loads(path.read_text(encoding="utf-8"))
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    assert not cell["outputs"] and cell["execution_count"] is None, path
