"""Inventory the proposed Nimbus deployment before implementing the readiness gates.

Run: uv run python checkpoints/05_production_readiness/starter.py --mock
Expected: hosting choice and unchecked gates. Cost/resources: $0, none.
"""

from common.lessons import complete, lesson_settings
from common.production_lessons import choose_host


def main():
    lesson_settings()
    print(choose_host(seconds=25, streaming=False, managed_sessions=False, local=False))
    # YOUR CODE HERE: run quality, identity, policy and local hosting gates before release.
    print(
        {
            "quality": "unchecked",
            "auth": "unchecked",
            "policy": "unchecked",
            "deployment": "unverified",
        }
    )
    complete()


if __name__ == "__main__":
    main()
