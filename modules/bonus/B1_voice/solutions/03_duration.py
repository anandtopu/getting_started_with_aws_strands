"""Reject sessions outside a one-to-thirty second budget. Run: uv run python
modules/bonus/B1_voice/solutions/03_duration.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return type(value) is int and 1 <= value <= 30


def main():
    print(solve(30))


if __name__ == "__main__":
    main()
