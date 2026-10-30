"""Fail a release for any breached or unjudged test. Run: uv run python
modules/bonus/B4_whats_new/solutions/03_breach.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return value["breaches"] == 0 and value["errors"] == 0


def main():
    print(solve({"breaches": 0, "errors": 0}))


if __name__ == "__main__":
    main()
