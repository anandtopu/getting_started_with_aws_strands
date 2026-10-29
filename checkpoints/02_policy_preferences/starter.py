"""Runnable local-search baseline for the Tier 2 checkpoint.

Run: uv run python checkpoints/02_policy_preferences/starter.py --mock
Expected: policy chunks. Cost/resources: local fixtures, $0.
"""

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.retrieval import lexical_search, load_chunks


def main() -> None:
    lesson_settings()
    console.print([c.record() for c in lexical_search(load_chunks(), "refund timing")])
    # YOUR CODE HERE: add validated answers, scoped preference/session storage,
    # a held-out evaluation report and deletion that preserves other customers.
    complete()


if __name__ == "__main__":
    run_cli(main)
