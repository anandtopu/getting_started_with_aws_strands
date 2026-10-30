"""Runnable Nimbus Support Copilot baseline. Run: uv run python
capstones/04_nimbus_support_copilot/starter.py --mock.
Expected: unchecked criteria. Cost $0; no resources. Implement the README acceptance criteria."""

from common.lessons import complete, lesson_settings


def readiness() -> dict:
    # YOUR CODE HERE: collect real evidence before changing any unchecked field.
    return {"evidence_checked": False, "boundaries_checked": False, "cleanup_checked": False}


def main() -> None:
    lesson_settings()
    print(readiness())
    complete()


if __name__ == "__main__":
    main()
