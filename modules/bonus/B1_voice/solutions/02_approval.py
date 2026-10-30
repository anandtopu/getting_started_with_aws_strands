"""Spoken approval must still require trusted review. Run: uv run python
modules/bonus/B1_voice/solutions/02_approval.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return "pending_human_review"


def main():
    print(solve("yes"))


if __name__ == "__main__":
    main()
